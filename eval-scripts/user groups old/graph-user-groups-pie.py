import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from matplotlib import cm


with open('data-user-groups.csv', 'r') as in_file:
    data = []
    line = in_file.readline()
    for d in line.strip().split(','):
        data.append(int(d))

fig = plt.figure(figsize=(8, 4))

ax = fig.add_subplot(111, aspect='equal')
labels = ('Watch', 'Only dismiss', 'No activity')
cs = cm.Vega20b(np.arange(3)/3.)
patches, texts, autotexts = plt.pie(data, labels=labels, autopct='%1.1f%%', colors=cs, startangle=90)
autotexts[0].set_color('w')


with PdfPages('user-groups-pie.pdf') as pdf:
    pdf.savefig(fig)

plt.close()
