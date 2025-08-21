
# Project Imports
from framework.example.signal.signalGenerator import SignalGenerator

# Third-Party Imports
import matplotlib.pyplot as plt


signalGenerator = SignalGenerator(name="MyFirstSignal")

signal = signalGenerator(None, length=50, period=20)
fig, ax = plt.subplots()
ax.plot(signal, linewidth=2.0)
plt.show()

signal = signalGenerator(None, length=50, period=20, noise="little")
fig, ax = plt.subplots()
ax.plot(signal, linewidth=2.0)
plt.show()

signal = signalGenerator(None, noise="much")
fig, ax = plt.subplots()
ax.plot(signal, linewidth=2.0)
plt.show()
