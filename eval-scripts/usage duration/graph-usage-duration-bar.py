import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from collections import defaultdict
import datetime


fist_n_days = 10

def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 5+height,
                '%d' % int(height),
                ha='center', va='bottom')

with open('data-usage-duration.csv', 'r') as in_file:
    data = defaultdict(int)
    for line in in_file:
        user_id, start_date_str, end_date_str = line.strip().split(',')
        if len(start_date_str) + len(end_date_str) == 0:
            print("Failed with", user_id, start_date_str, end_date_str)
            continue
        # start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%f')
        # end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S.%f')
        start_date = datetime.datetime.strptime(start_date_str[:10], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str[:10], '%Y-%m-%d')
        time_diff = end_date - start_date
        data[time_diff.days] += 1
    print(data)

fig = plt.figure(figsize=(8, 4))

ax = fig.add_subplot(111)
ax.set_xlabel('Usage Period (in Days)')
ax.set_ylabel('Number of Users')
# old
# ind = [k+1 for k in data.keys()]
# values = list(data.values())

# new (aggregated)
ind = [k+1 for k in data.keys()][:fist_n_days]
later_ind = min([k+1 for k in data.keys() if k+1 > max(ind)])
values = []
agg_value = 0
for key, value in data.items():
    if key+1 in ind:
        print('add', value, 'for', key + 1)
        values.append(value)
    else:
        agg_value += value

values.append(agg_value)
ind += [later_ind]

print(ind, values, len(ind), len(values))

rects = plt.bar(ind, values, fill=None, hatch='\\\\\\\\\\', tick_label=ind)

autolabel(rects)
plt.ylim(0,400)
plt.yticks(range(0,400,50))

labels = [item.get_text() for item in ax.get_xticklabels()]
labels[-1] = str(later_ind) + '+'
ax.set_xticklabels(labels)

plt.tight_layout()

with PdfPages('usage_duration_bar.pdf') as pdf:
    pdf.savefig(fig)

plt.close()
