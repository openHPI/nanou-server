import datetime
from collections import defaultdict
from operator import itemgetter


data = defaultdict(lambda: defaultdict(int))
with open('data-watch-activity.csv') as in_file:
    for line in in_file:
        date_str = line.strip()
        if len(date_str) > 0:
            date_str = date_str[:-3] + date_str[-2:]
            date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            data[date.weekday()][date.hour] += 1

for weekday in range(0,7):
    values = [data[weekday][hour] for hour in range(0,24)]
    values = [weekday] + values
    print(' & '.join(str(v) for v in values), '\\\\')
