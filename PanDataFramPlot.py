import matplotlib.pyplot as plt
import pandas as pd

df = pd.DataFrame({"begin": [1,4,6,9], "end" : [3,5,8,12]})

fig, ax = plt.subplots()

for x_1 , x_2 in zip(df['begin'].values ,df['end'].values):
    ax.add_patch(plt.Rectangle((x_1,0),x_2-x_1,0.5))

ax.autoscale()
ax.set_ylim(-2,2)
plt.show()
