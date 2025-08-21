
# Project Imports
from framework.example.solar.Database import Database

# Third-Party Imports
import matplotlib.pyplot as plt


db = Database(name="DB")

data = db.read(key="app130/solar")
data_values = [date["value"] for date in data]

fig, ax = plt.subplots()
ax.plot(data_values, linewidth=2.0)
plt.show()
