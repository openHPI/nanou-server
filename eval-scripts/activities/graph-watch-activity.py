import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from collections import defaultdict
import datetime


data = defaultdict(lambda: defaultdict(int))
with open('data-watch-activity.csv') as in_file:
    for line in in_file:
        date_str = line.strip()
        if len(date_str) > 0:
            date_str = date_str[:-3] + date_str[-2:]
            date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            data[date.weekday()][date.hour] += 1



h_data = np.array([[data[weekday][hour] for hour in range(0,24)] for weekday in range(0,7)])
heat_data = (h_data - h_data.mean()) / (h_data.max() - h_data.min())


fig = plt.figure(figsize=(8, 3))

ax = fig.add_subplot(111)

###
heatmap = ax.pcolor(heat_data, cmap=plt.cm.Blues , alpha=0.8)

# Format
fig = plt.gcf()

# ax.set_frame_on(False)

# put the major ticks at the middle of each cell
ax.set_yticks(np.arange(heat_data.shape[0]) + 0.5, minor=False)
ax.set_xticks(np.arange(heat_data.shape[1]) + 0.5, minor=False)

# want a more natural, table-like display
ax.invert_yaxis()
# ax.xaxis.tick_top()
# ax.xaxis.set_label_position('top')

# Set the labels
xlabels = range(0, 24)
ylabels = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
]
ax.set_xticklabels(xlabels, minor=False)
ax.set_yticklabels(ylabels, minor=False)
###

ax.set_xlabel('Hour of the Day')
ax.set_ylabel('Weekday')

plt.tight_layout()

with PdfPages('graph-watch-activities-weekday.pdf') as pdf:
    pdf.savefig(fig)

plt.close()
