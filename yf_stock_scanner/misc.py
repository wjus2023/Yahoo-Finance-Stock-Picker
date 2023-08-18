import robin_stocks.robinhood as r
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np

def show_plot_four(price, firstIndicator, secondIndicator, thirdIndicator, fourthIndicator, dates, symbol="", label1="", label2="", label3="", label4=""):
    plt.figure(figsize=(10,5))
    plt.title(symbol)
    plt.plot(dates, price, label="Closing prices", marker='o', markersize=2, color = 'blue')
    plt.plot(dates, firstIndicator, label=label1, color = 'red')
    plt.plot(dates, secondIndicator, label=label2, color = 'green')
    plt.plot(dates, thirdIndicator, label=label3, linestyle='--', linewidth=1, color = 'orange')
    plt.plot(dates, fourthIndicator, label=label4, linestyle='--', linewidth=1, color = 'purple')
    plt.yticks(np.arange(price.min(), price.max(), step=((price.max()-price.min())/15.0)))
    plt.legend()
    filename = symbol
    plt.show()

