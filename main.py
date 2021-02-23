import srt
import sys
import datetime

original_filename = sys.argv[1]
adjusted_filename = sys.argv[2]

first_commercial_duration = datetime.timedelta(seconds=29)
following_commercial_duration = datetime.timedelta(seconds=118)

with open(original_filename, 'r') as sub_file:
    sub_file_text = sub_file.read()

parsed_subtitles = list(srt.parse(sub_file_text))

adjusted_subtitles = []
adjusted_index = 1

first_sub_found = False
current_time = datetime.timedelta(seconds=0)
previous_time = datetime.timedelta(seconds=0)
total_commerical_time = datetime.timedelta(seconds=0)

for sub in parsed_subtitles:
    current_time = sub.start

    if current_time > first_commercial_duration and first_sub_found == False:
        total_commerical_time += first_commercial_duration
        first_sub_found = True
    elif current_time - previous_time > following_commercial_duration:
        total_commerical_time += following_commercial_duration
    
    if first_sub_found == True:
        adjusted_subtitles.append(srt.Subtitle(index=adjusted_index, start=sub.start - total_commerical_time, end=sub.end - total_commerical_time, content=sub.content))
        adjusted_index += 1

    previous_time = current_time

with open(adjusted_filename, 'w') as new_sub_file:
    new_sub_file.write(srt.compose(adjusted_subtitles))
