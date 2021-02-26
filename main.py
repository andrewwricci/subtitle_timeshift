import argparse
import datetime
import os
import srt

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
    else:
        return original_files

def parse_subtitle_file(original_file_location):
    with open(original_file_location, 'r') as sub_file:
        sub_file_text = sub_file.read()

    parsed_subtitles_text = list(srt.parse(sub_file_text))
    return parsed_subtitles_text

def adjust_total_commerical_duration(current_sub, prior_sub, commerical_duration, total_commercial_time, auto_adjust):
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
    parser.add_argument('-a', '--adjusted_file_suffix', required=False,
                        help='New file suffix for adjusted files. Leave blank to overwrite originals')
    parser.add_argument('-first', '--first_commercial_duration', required=True,
                        help='Length of expected first commerical break in seconds. Will remove all subtitles before this value. Set to 0 if no initial commercial expected.')
    parser.add_argument('-following', '--following_commercial_duration', required=True,
                        help='Length of expected other commerical breaks in seconds. If setting manually, set this to value less than or equal to expected breaks.')
    parser.add_argument('-auto', '--auto_adjust_file', required=False,
                        help='Controls whether script will auto-adjust times based on inputted duration or allow user control')

    args = parser.parse_args()

    first_commercial_duration = datetime.timedelta(seconds=int(args.first_commercial_duration))
    following_commercial_duration = datetime.timedelta(seconds=int(args.following_commercial_duration))

    if args.auto_adjust_file == "true":
        auto_adjust_subs = True
    else:
        auto_adjust_subs = False

    if args.original_file == "ALL":
        original_file_value = os.path.dirname(os.path.realpath(__file__))
    else:
        original_file_value = args.original_file

    original_file_list = get_subtitle_files_list(original_file_value)

    for original_file in original_file_list:
        print("Beginning adjustment of file {file}".format(file=original_file))
        parsed_subtitles = parse_subtitle_file(original_file)

        adjusted_subtitles = []
        adjusted_index = 1

        first_sub_found = False
        total_commerical_time = datetime.timedelta(seconds=0)
        previous_time = datetime.timedelta(seconds=0)
        previous_sub = srt.Subtitle(index=0, start=0, end=0, content="No first subtitle detected")

        for sub in parsed_subtitles:
            current_time = sub.start

            if current_time > first_commercial_duration and first_sub_found is False:
                total_commerical_time = adjust_total_commerical_duration(sub, previous_sub, first_commercial_duration, 
                                                                         total_commerical_time, True)
                first_sub_found = True
            elif current_time - previous_time > following_commercial_duration:
                total_commerical_time = adjust_total_commerical_duration(sub, previous_sub, following_commercial_duration, 
                                                                         total_commerical_time, auto_adjust_subs)

            if first_sub_found is True:
                adjusted_subtitles.append(srt.Subtitle(index=adjusted_index, start=sub.start - total_commerical_time,
                                                       end=sub.end - total_commerical_time, content=sub.content))
                adjusted_index += 1

            previous_time = current_time
            previous_sub = sub

        if args.adjusted_file_suffix:
            original_file_name_base = original_file.split('.srt')[0]
            final_file_name = original_file_name_base + args.adjusted_file_suffix + '.srt'
        else:
            final_file_name = original_file
        with open(final_file_name, 'w') as new_sub_file:
            new_sub_file.write(srt.compose(adjusted_subtitles))

if __name__ == '__main__':
    main()
