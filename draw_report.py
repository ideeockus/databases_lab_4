import datetime
import json

import matplotlib.pyplot as plt
import seaborn as sns


data = None
with open('monitoring_data.json', 'r') as f:
    data = json.loads(f.read())

x = [datetime.datetime.fromtimestamp(s['ts']) for s in data]
y = [s['state'] for s in data]
instance_port = [s['instance_port'] for s in data]

# sns.lineplot(x=x, y=y, hue=instance_port)


_instances = ['5433', '5434', '5435']
colors = ['green', 'blue', 'red']

def get_yvalue(n: int) -> int:
    return {
        2: 0,
        1: 1,
        0: 2,
    }.get(n, n)

def fmt_yticks(n: int) -> str:
    return {
        2: 'OK',
        1: 'FAIL',
        0: 'DOWN',
    }.get(n, '')

sns.set(rc={'figure.figsize':(25, 5)})
fig, axs = plt.subplots(ncols=3)
for i in range(3):
    pl = sns.lineplot(
        x=[datetime.datetime.fromtimestamp(s['ts']) for s in filter(lambda m: _instances[i] == m['instance_port'], data)], 
        y=[get_yvalue(s['state']) for s in filter(lambda m: _instances[i] == m['instance_port'], data)], 
        ax=axs[i],
        color=colors[i],
    )
    yticks = pl.get_yticks()
    pl.set_yticklabels([fmt_yticks(tick) for tick in yticks])

fig.savefig('out.png')