import numpy as np
import pandas as pd
import ta as ta
import os
import yfinance as yf
import matplotlib.pyplot as plt
from misc import *
from matplotlib import style
from datetime import datetime, timedelta
style.use('ggplot')

# Data Directory
directory_path = 'data'

def get_last_crossing(df, days, symbol="", direction=""):
    prices = df.loc[:,"Price"]
    shortTerm = df.loc[:,"Indicator1"]
    LongTerm = df.loc[:,"Indicator2"]
    dates = df.loc[:,"Dates"]
    lastIndex = prices.size - 1
    index = lastIndex
    found = index
    
    #define wlp
    wlp = 0
    recentDiff = (shortTerm.at[index] - LongTerm.at[index]) >= 0
    if((direction == "above" and not recentDiff) or (direction == "below" and recentDiff)):
        return 0
    index -= 1
    while(index >= 0 and found == lastIndex and not np.isnan(shortTerm.at[index]) and not np.isnan(LongTerm.at[index]) \
                        and ((pd.Timestamp("now", tz='US/Pacific') - dates.at[index]) <= pd.Timedelta(str(days) + " days"))):
        if(recentDiff):
            if((shortTerm.at[index] - LongTerm.at[index]) < 0):
                found = index
        else:
            if((shortTerm.at[index] - LongTerm.at[index]) > 0):
                found = index
        index -= 1
    if(found != lastIndex):
        if((direction == "above" and recentDiff) or (direction == "below" and not recentDiff)):
            wlp = (((prices.at[lastIndex] - prices.at[found]) / prices.at[found]) + wlp) * 100
            print(symbol + ": Golden Cross found on " + str(dates.at[found+1]).split(' ')[0]) 
            print("price at cross: " + str(round((prices.at[found]),2)) + " current price: " + str(round((prices.at[lastIndex]),2)))
            print("% since crossed: " + str(round(wlp,2)) + "%")

        return (1 if recentDiff else -1)
    else:
        return 0


def golden_cross(n1, n2, n3, n4, days, direction=""):

    #Open File
    csv_write_flag = 0  
    file_list = os.listdir(directory_path)
    for filename in file_list:
        if os.path.isfile(os.path.join(directory_path, filename)):
            with open(os.path.join(directory_path, filename), 'r') as file:
                stockTicker = filename.split('_')[0]
                df = pd.read_csv(os.path.join(directory_path, filename))
                
                #Couldn't get pricing data
                if(df is None or None in df):
                    return False

                closingPrices = df['Price']
                dates = df['Dates']
                indx_end = len(df.index)
 
                date_time_string = df['Dates'][len(df)-1]
                most_updated_date = date_time_string.split(' ')[0]
                date_curr = datetime.today().date()
                
                
                most_updated_date = datetime.strptime(most_updated_date, "%Y-%m-%d")
                most_updated_date = most_updated_date.date()
                
                end_date = date_curr + timedelta(days=1)
               
                if date_curr > most_updated_date:   
                    df.drop(df.tail(1).index, inplace=True)
                    
                    if stockTicker == 'GSPC':
                        stockTicker = '^GSPC'
                    tick = yf.Ticker(stockTicker)
                    
                    data = tick.history(start=most_updated_date, end=end_date, interval='1d')
                    Date = data.index
                    indx = list(range(indx_end,indx_end+len(data)))
                    indic1 = list(range(1, len(data)+1))
                    indic2 = list(range(2, len(data)+2))
                    indic3 = list(range(3, len(data)+3))
                    indic4 = list(range(4, len(data)+4))

                    data.index = indx
                    
                    df_yf = {'Price': data['Close'], 'Indicator1': indic1, 'Indicator2': indic2, 'Indicator3': indic3, 'Indicator4': indic4, 'Dates': Date}
                    df_yf = pd.DataFrame(df_yf)

                    df_updated = pd.concat([df, df_yf])
                    df_updated = df_updated.reset_index(drop=True)
                    print(stockTicker)
                    csv_write_flag = 1
                  
                    #Combined Dataframe - df_updated
                    closingPrices = df_updated['Price']
                    dates = df_updated['Dates']
                
                else:
                    csv_write_flag = 0

                if date_curr == most_updated_date:
                    if stockTicker == 'GSPC':
                        stockTicker = '^GSPC'
                    tick = yf.Ticker(stockTicker)

                    latest_data = tick.history(start=date_curr, end=end_date, interval='1d')
                    max_indx = len(closingPrices)
                    
                    pd.options.mode.chained_assignment = None
                    closingPrices[max_indx-1] = latest_data['Close'][0]
                    csv_write_flag = 1
               
                price = pd.Series(closingPrices)
                dates = pd.Series(dates)
                dates = pd.to_datetime(dates)

                sma1 = ta.volatility.bollinger_mavg(price, int(n1), False)
                sma2 = ta.volatility.bollinger_mavg(price, int(n2), False)
                sma3 = ta.volatility.bollinger_mavg(price, int(n3), False)
                sma4 = ta.volatility.bollinger_mavg(price, int(n4), False)

                series = [price.rename("Price"), sma1.rename("Indicator1"), sma2.rename("Indicator2"), sma3.rename("Indicator3"), sma4.rename("Indicator4"), dates.rename("Dates")]
                df = pd.concat(series, axis=1)
                
                if stockTicker == '^GSPC':
                    stockTicker = 'GSPC'
                if csv_write_flag:
                    df.to_csv('data/%s_data.csv' % stockTicker)

                cross = get_last_crossing(df, days, symbol=stockTicker, direction=direction)

                if cross:
                    get_rsi(stockTicker, 14)
                    print("-------------------------------------------------------------------")
                    print("-------------------------------------------------------------------")
                    show_plot_four(price, sma1, sma2, sma3, sma4, dates, symbol=stockTicker, label1=str(n1)+" day SMA", label2=str(n2)+" day SMA", label3=str(n3)+" day SMA", label4=str(n4)+" day SMA")
                    

def get_rsi(stockTicker, days):
    file_list = os.listdir(directory_path)
    for filename in file_list:
        if os.path.isfile(os.path.join(directory_path, filename)):
            if filename == stockTicker + "_data.csv":
                with open(os.path.join(directory_path, filename), 'r') as file:
                    stockTicker = filename.split('_')[0]
                    df = pd.read_csv(os.path.join(directory_path, filename))
    
                    dates = pd.Series(df['Dates'])
                    price = pd.Series(df['Price'])
                    ret = price.diff()
                    up = []
                    down = []
                    for i in range(len(ret)):
                        if ret[i] < 0:
                            up.append(0)
                            down.append(ret[i])
                        else:
                            up.append(ret[i])
                            down.append(0)
                    up_series = pd.Series(up)
                    down_series = pd.Series(down).abs()
                    up_ewm = up_series.ewm(com = days - 1, adjust = False).mean()
                    down_ewm = down_series.ewm(com = days - 1, adjust = False).mean()
                    rs = up_ewm/down_ewm
                    rsi = 100 - (100 / (1 + rs))
                    rsi_df = pd.DataFrame(rsi).rename(columns = {0:'rsi'}).set_index(price.index)
                    rsi_df = rsi_df.dropna()
                    rsi_signal = []
                    signal = 0
                    for i in range(len(rsi_df)):
                        rsi_signal.append(rsi_df.iloc[i]['rsi'])

                    print("RSI: ", round(rsi_signal[len(rsi_signal) - 1], 2))
                    return rsi_signal[len(rsi_signal) - 1]
    

def main():  
    print("---------------------------------")
    print("---------------------------------")
    print("------------Foward---------------")
    print("----Scanning... Please Hold -----")
    history = golden_cross(n1=12, n2=26, n3=50, n4=200, days=5, direction="above")
    print("---------------------------------")
    print("---------------------------------")
    print("-----------Completed-------------")
    print("---------------------------------")
    





if __name__ =="__main__":
    main()    



