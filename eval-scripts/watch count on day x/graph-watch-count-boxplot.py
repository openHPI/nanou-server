import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from collections import defaultdict
import datetime



# user -> usage_day -> value
pre_data = defaultdict(lambda: defaultdict(int))
with open('data-watch-count.csv', 'r') as in_file:
    for line in in_file:
        user_id, first_act_str, dat_str, watch_count = line.strip().split(',')
        if len(first_act_str) == 0:
            print("Failed with", user_id, first_act_str, dat_str, watch_count)
            continue
        elif len(dat_str) == 0:
            first_act = datetime.datetime.strptime(first_act_str, '%Y-%m-%d')
            dat = first_act
        else:
            first_act = datetime.datetime.strptime(first_act_str, '%Y-%m-%d')
            dat = datetime.datetime.strptime(dat_str, '%Y-%m-%d')
        time_diff = dat - first_act
        pre_data[user_id][time_diff.days] += int(watch_count)
        # print("add", user_id, time_diff.days, watch_count)

date_range = 16
data = []
for day in range (0, date_range):
    values = []
    for user, value_dict in pre_data.items():
        value = value_dict[day]
        if value > 0:
            values.append(value)
    data.append(values)
# print(data)

fig = plt.figure(figsize=(8, 4))

ax = fig.add_subplot(111)
ax.set_xlabel('Day of Usage')
ax.set_ylabel('Watched Videos')
labels = range(1, date_range+1)
plt.boxplot(data, 0, labels=labels, medianprops={'color': 'k'})

plt.tight_layout()

with PdfPages('watched_videos_boxplot.pdf') as pdf:
    pdf.savefig(fig)

plt.close()
