import argparse
import datetime
import json
import os
import srt

class Subtitle:
    def __init__(self):
        self.index = 1
        self.subtitles = []
        self.first_sub_found = False
        self.total_commerical_time = datetime.timedelta(seconds=0)

def get_subtitle_files_list(original_file_location):
    original_files = []

    if os.path.isdir(original_file_location):
        directory_name = original_file_location
        for file in os.listdir(directory_name):
            if file.endswith(".srt"):
                original_files.append(directory_name + "/" + file)
    else:
        original_files.append(original_file_location)

    if not original_files:
        raise ValueError("No valid .srt files found at {original_file}".format(original_file=original_file_location))

    return original_files

def parse_subtitle_file(original_file_location):
    with open(original_file_location, 'r') as sub_file:
        sub_file_text = sub_file.read()

    parsed_subtitles_text = list(srt.parse(sub_file_text))
    return parsed_subtitles_text

def adjust_total_commerical_duration(current_sub, prior_sub, commerical_duration, total_commercial_time, auto_adjust, first_sub):
    if first_sub:
        print("Detected first subtitle - Index: {index} Timestamp: {timestamp} Content: {content}".format(index=current_sub.index,
                                                                                                         timestamp=current_sub.start,
                                                                                                         content=current_sub.content))
        print("All prior subtitles will be removed")
    else:
        print("Commerical period detected between the following subtitles:")
        print("First subtitle - Index: {index} Timestamp: {timestamp} Content: {content}".format(index=prior_sub.index,
                                                                                                timestamp=prior_sub.start - total_commercial_time,
                                                                                                content=prior_sub.content))
        print("Second subtitle - Index: {index} Timestamp: {timestamp} Content: {content}".format(index=current_sub.index,
                                                                                                timestamp=current_sub.start - total_commercial_time,
                                                                                                content=current_sub.content))
    if auto_adjust is True:
        total_commercial_time += commerical_duration
    else:
        seconds_input = input("Please enter the number of seconds to subtract from all subtitles after the first subtitle: ")
        commerical_duration = datetime.timedelta(seconds=int(seconds_input))
        total_commercial_time += commerical_duration
    print("All remaining subtitles moved -{commerical_duration}".format(commerical_duration=commerical_duration))

    return total_commercial_time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--original_file', required=True,
                        help='Original file(s) to edit. Use folder name (or ALL for current folder) to include all files in folder')
    parser.add_argument('-a', '--new_file_suffix', required=False,
                        help='New file suffix for edited files. Leave blank to overwrite originals')
    parser.add_argument('-first', '--first_commercial_duration', required=False,
                        help='Length of expected first commerical break in seconds. Will remove all subtitles before this value. Set to 0 if no initial commercial expected.')
    parser.add_argument('-following', '--following_commercial_duration', required=False,
                        help='Length of expected other commerical breaks in seconds. If setting manually, set this to value less than or equal to expected breaks.')
    parser.add_argument('-json', '--json_break_file', required=False,
                        help='File containing breaks in json format. See example.json file for formatting')
    parser.add_argument('-auto', '--auto_adjust_file', required=False, action=argparse.BooleanOptionalAction,
                        help='Controls whether script will auto-adjust times based on inputted duration or allow user control')

    args = parser.parse_args()

    auto_adjust_subs = bool(args.auto_adjust_file)

    if args.original_file == "ALL":
        original_file_value = os.path.dirname(os.path.realpath(__file__))
    else:
        original_file_value = args.original_file

    original_file_list = get_subtitle_files_list(original_file_value)

    for original_file in original_file_list:
        if args.first_commercial_duration and args.following_commercial_duration:
            first_commercial_duration = datetime.timedelta(seconds=int(args.first_commercial_duration))
            following_commercial_string_list = args.following_commercial_duration.split(",")
            following_commercial_duration = [datetime.timedelta(seconds=int(i)) for i in following_commercial_string_list]
        elif args.json_break_file:
            json_file = open(args.json_break_file)
            commercial_breaks_definition = json.load(json_file)
            file_name = original_file.split("/")[-1]
            file_definition = commercial_breaks_definition.get(file_name, None)
            if file_definition:
                first_commercial_duration = datetime.timedelta(seconds=int(file_definition["first"]))
                following_commercial_int_list = file_definition["following"]
            else:
                first_commercial_duration = datetime.timedelta(seconds=int(commercial_breaks_definition["*"]["first"]))
                following_commercial_int_list = commercial_breaks_definition["*"]["following"]
            following_commercial_duration = [datetime.timedelta(seconds=i) for i in following_commercial_int_list]
        else:
            raise ValueError("Please set commerical durations in either json or script arguments")

        following_commercial_position = 0
        following_commercial_final_position = len(following_commercial_duration) - 1

        print("Beginning analysis of file {file}".format(file=original_file))
        parsed_subtitles = parse_subtitle_file(original_file)

        new_subtitle = Subtitle()

        previous_time = datetime.timedelta(seconds=0)
        previous_sub = srt.Subtitle(index=0, start=0, end=0, content="No first subtitle detected")

        for sub in parsed_subtitles:
            current_time = sub.start
            following_commercial_duration_value = following_commercial_duration[following_commercial_position]

            if current_time > first_commercial_duration and new_subtitle.first_sub_found is False:
                first_subtitle = True
                new_subtitle.total_commerical_time = adjust_total_commerical_duration(sub, previous_sub, first_commercial_duration,
                                                                         new_subtitle.total_commerical_time, True, first_subtitle)
                new_subtitle.first_sub_found = True
            elif current_time - previous_time > following_commercial_duration_value:
                first_subtitle = False
                new_subtitle.total_commerical_time = adjust_total_commerical_duration(sub, previous_sub, following_commercial_duration_value,
                                                                         new_subtitle.total_commerical_time, auto_adjust_subs, first_subtitle)
                if following_commercial_position < following_commercial_final_position:
                    following_commercial_position += 1

            if new_subtitle.first_sub_found is True:
                new_subtitle.subtitles.append(srt.Subtitle(index=new_subtitle.index, start=sub.start - new_subtitle.total_commerical_time,
                                                       end=sub.end - new_subtitle.total_commerical_time, content=sub.content))
                new_subtitle.index += 1

            previous_time = current_time
            previous_sub = sub

        if args.new_file_suffix:
            original_file_name_base = original_file.split('.srt')[0]
            final_file_name = original_file_name_base + args.new_file_suffix + '.srt'
        else:
            final_file_name = original_file
        with open(final_file_name, 'w') as new_sub_file:
            new_sub_file.write(srt.compose(new_subtitle.subtitles))

if __name__ == '__main__':
    main()
