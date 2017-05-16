import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from collections import defaultdict
import datetime

def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 5+height,
                '%d' % int(height),
                ha='center', va='bottom')


with open('data-day-of-usage.csv', 'r') as in_file:
    data = defaultdict(int)
    for line in in_file:
        day, value = line.strip().split(',')
        data[int(day)] += int(value)
    print(data)

fig = plt.figure(figsize=(8, 4))

ax = fig.add_subplot(111)
ax.set_xlabel('Overall Days of Usage')
ax.set_ylabel('Number of Users')
ind = [k for k in data.keys()]
values = list(data.values())


rects = plt.bar(ind, values, fill=None, hatch='/////', tick_label=ind)

autolabel(rects)
plt.ylim(0,375)
plt.yticks(range(0,375,50))

plt.tight_layout()

with PdfPages('days_of_usage_bar.pdf') as pdf:
    pdf.savefig(fig)

plt.close()
