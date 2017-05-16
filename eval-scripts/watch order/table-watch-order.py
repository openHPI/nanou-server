import datetime
from collections import defaultdict
from operator import itemgetter

first_n_watch_places = 5
first_n_videos = 20

video_dep_count = {}
with open('data-video-dep-count.csv') as in_file:
    for line in in_file:
        video_id, count = line.strip().split(',')
        video_dep_count[video_id] = int(count)

user_videos_data = defaultdict(list)
with open('data-watch-order.csv') as in_file:
    for line in in_file:
        user_id, video_id, date_str = line.strip().split(',')
        if len(date_str) > 0:
            date_str = date_str[:-3] + date_str[-2:]
            date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            user_videos_data[user_id].append((video_id, date))

data = defaultdict(lambda: {i: 0 for i in range(0, first_n_watch_places+1)})
for user_id, videos in user_videos_data.items():
    sorted_videos = [itemgetter(0)(v) for v in sorted(videos, key=itemgetter(1))]
    for i, video_id in enumerate(sorted_videos):
        watch_index = min(i, first_n_watch_places)
        data[video_id][watch_index] += 1

# print({video_id: sum(counts.values()) for video_id, counts in data.items()})
print('video name\t& overall count\t& dep count\t& 1\t\t& 2\t\t& 3\t\t& 4\t\t& 5\t\t& later \\\\ \\hline')
sorted_videos = sorted(data, key=lambda x: -1*sum(data[x].values()))
watch_counts =  {i: 0 for i in range(0, first_n_watch_places+1)}
for d in sorted_videos:
    for i in range(first_n_watch_places+1):
        watch_counts[i] += data[d][i]
for d in sorted_videos:  # [:first_n_videos]:
    vals = [data[d][i] for i in range(first_n_watch_places+1)]
    vals2 = [val*100.0/watch_counts[i] for i, val in enumerate(vals)]
    print('%s\t\t& %d\t\t& %d\t\t& %.2f\\%%\t& %.2f\\%%\t& %.2f\\%%\t& %.2f\\%%\t& %.2f\\%%\t& %.2f\\%% \\\\' % tuple([d, sum(vals), video_dep_count[d]] + vals2))
