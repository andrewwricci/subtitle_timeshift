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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--original_file', required=True, help='Original file(s) to edit. Use folder name (or ALL for current folder) to include all files in folder')
    parser.add_argument('-a', '--adjusted_file_suffix', required=False, help='New file suffix for adjusted files. Leave blank to overwrite originals')
    parser.add_argument('-first', '--first_commercial_duration', required=True, help='Length of first commerical break in seconds')
    parser.add_argument('-following', '--following_commercial_duration', required=True, help='Length of following commerical breaks in seconds')

    args = parser.parse_args()

    first_commercial_duration = datetime.timedelta(seconds=int(args.first_commercial_duration))
    following_commercial_duration = datetime.timedelta(seconds=int(args.following_commercial_duration))

    if args.original_file == "ALL":
        original_file_value = os.path.dirname(os.path.realpath(__file__))
    else:
        original_file_value = args.original_file

    original_file_list = get_subtitle_files_list(original_file_value)

    for original_file in original_file_list:
        parsed_subtitles = parse_subtitle_file(original_file)

        adjusted_subtitles = []
        adjusted_index = 1

        first_sub_found = False
        current_time = datetime.timedelta(seconds=0)
        previous_time = datetime.timedelta(seconds=0)
        total_commerical_time = datetime.timedelta(seconds=0)

        for sub in parsed_subtitles:
            current_time = sub.start

            if current_time > first_commercial_duration and first_sub_found is False:
                total_commerical_time += first_commercial_duration
                first_sub_found = True
            elif current_time - previous_time > following_commercial_duration:
                total_commerical_time += following_commercial_duration

            if first_sub_found is True:
                adjusted_subtitles.append(srt.Subtitle(index=adjusted_index, start=sub.start - total_commerical_time, end=sub.end - total_commerical_time, content=sub.content))
                adjusted_index += 1

            previous_time = current_time

        if args.adjusted_file_suffix:
            original_file_name_base = original_file.split('.srt')[0]
            final_file_name = original_file_name_base + args.adjusted_file_suffix + '.srt'
        else:
            final_file_name = original_file
        with open(final_file_name, 'w') as new_sub_file:
            new_sub_file.write(srt.compose(adjusted_subtitles))

if __name__ == '__main__':
    main()
