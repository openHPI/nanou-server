import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from operator import itemgetter

from collections import defaultdict
import datetime

def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    print("rects", rects)
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 0.01+height,
                '%.2f' % (height),
                ha='center', va='bottom')

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

date_range = 16
data = []
for day in range (0, date_range):
    values = []
    for user, value_dict in pre_data.items():
        value = value_dict[day]
        values.append(value)
    print(values)
    avg = sum(values)/len(values) if len(values) > 0 else 0
    print(sum(values), len(values), avg)
    data.append(avg)

fig = plt.figure(figsize=(8, 4))

ax = fig.add_subplot(111)
ax.set_xlabel('Day of Usage')
ax.set_ylabel('Avg. Watched Videos')
ind = range(1, date_range+1)
values = data
rects = plt.bar(ind, values, fill=None, hatch='/////', tick_label=ind)

autolabel(rects)
plt.ylim(0,0.8)
plt.yticks([i*1.0/10.0 for i in range(0,8)])

plt.tight_layout()

with PdfPages('watched_videos_bar.pdf') as pdf:
    pdf.savefig(fig)

plt.close()
