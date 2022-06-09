import streamlit as st
import backtrader as bt
import yfinance as yf
import pandas as pd
import pandas_datareader as pdr
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import warnings
import os
from matplotlib import warnings
from matplotlib.dates import (HOURS_PER_DAY, MIN_PER_HOUR, SEC_PER_MIN)
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as bs
from rsi import RSIStrategy
from datetime import date, timedelta, datetime
from patterns import candlestick_patterns
import streamlit as st
import requests
import os
import sys
import subprocess

# check if the library folder already exists, to avoid building everytime you load the pahe
if not os.path.isdir("/tmp/ta-lib"):

    # Download ta-lib to disk
    with open("/tmp/ta-lib-0.4.0-src.tar.gz", "wb") as file:
        response = requests.get(
            "http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz"
        )
        file.write(response.content)
    # get our current dir, to configure it back again. Just house keeping
    default_cwd = os.getcwd()
    os.chdir("/tmp")
    # untar
    os.system("tar -zxvf ta-lib-0.4.0-src.tar.gz")
    os.chdir("/tmp/ta-lib")
    os.system("ls -la /app/equity/")
    # build
    os.system("./configure --prefix=/home/appuser")
    os.system("make")
    # install
    os.system("make install")
    # back to the cwd
    os.chdir(default_cwd)
    sys.stdout.flush()

# add the library to our current environment
from ctypes import *

lib = CDLL("/home/appuser/lib/libta_lib.so.0.0.0")
# import library
try:
    import talib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--global-option=build_ext", "--global-option=-L/home/appuser/lib/", "--global-option=-I/home/appuser/include/", "ta-lib"])
finally:
    import talib
   
def fxn():
    warnings.warn("deprecated", DeprecationWarning)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()

st.set_option('deprecation.showPyplotGlobalUse', False)
today=date.today()
def backtestrsi():
    global strategy
    ticker=st.sidebar.text_input("Stock ticker", value="AAPL")
    start=st.sidebar.text_input("Start date", value="2018-01-31")
    end=st.sidebar.text_input("End date", value=today)
    cash=st.sidebar.text_input("Starting cash", value=10000)
    cash=int(cash)
    cerebro=bt.Cerebro()
    cerebro.broker.set_cash(cash)
    start_value=cash
    data = bt.feeds.PandasData(dataname=yf.download(ticker, start, end))
    start=start.split("-")
    end=end.split("-")
    for i in range(len(start)):
        start[i]=int(start[i])
    for j in range(len(end)):
        end[j]=int(end[j])
    year=end[0]-start[0]
    month=end[1]-start[1]
    day=end[2]-start[2]
    totalyear=year+(month/12)+(day/365)
    matplotlib.use('Agg')
    cerebro.adddata(data)

    cerebro.addstrategy(RSIStrategy)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    final_value=cerebro.broker.getvalue()
    returns=(final_value-start_value)*100/start_value
    annual_return=returns/totalyear
    returns=round(returns, 2)
    annual_return=round(annual_return,2)
    returns=str(returns)
    annual_return=str(annual_return)
    figure = cerebro.plot()[0][0]
    st.pyplot(figure)
    st.write('')
    st.subheader(f"{ticker}'s total returns are {returns}% with a {annual_return}% APY")
    strategy=''

def volatility():
    global strategy
    import backtrader as bt
    import os
    from VIXStrategy import VIXStrategy
    import yfinance as yf
    import pandas as pd
    global ticker
    ticker=st.sidebar.text_input("Stock ticker", value="AAPL")
    start=st.sidebar.text_input("Start date", value="2018-01-31")
    end=st.sidebar.text_input("End date", value=today)
    cash=st.sidebar.text_input("Starting cash", value=10000)
    cash=int(cash)
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(cash)
    start_value=cash
    class SPYVIXData(bt.feeds.GenericCSVData):
        lines = ('vixopen', 'vixhigh', 'vixlow', 'vixclose',)

        params = (
            ('dtformat', '%Y-%m-%d'),#'dtformat', '%Y-%m-%d'),
            ('date', 0),
            ('spyopen', 1),
            ('spyhigh', 2),
            ('spylow', 3),
            ('spyclose', 4),
            ('spyadjclose', 5),
            ('spyvolume', 6),
            ('vixopen', 7),
            ('vixhigh', 8),
            ('vixlow', 9),
            ('vixclose', 10)
        )

    class VIXData(bt.feeds.GenericCSVData):
            params = (
            ('dtformat', '%Y-%m-%d'),
            ('date', 0),
            ('vixopen', 1),
            ('vixhigh', 2),
            ('vixlow', 3),
            ('vixclose', 4),
            ('volume', -1),
            ('openinterest', -1)
        )
    #
    ticker=ticker
    df = yf.download(tickers=ticker, start=start, end=end, rounding= False)
    df=df.reset_index() 
    df2 = yf.download(tickers='^VIX', start=start, end=end, rounding= False)
    df2.rename(columns = {'Open':'Vix Open', 'High':'Vix High', 'Low':'Vix Low', 'Close':'Vix Close'}, inplace = True)
    df2=df2.drop("Volume", axis=1)
    df2=df2.drop("Adj Close", axis=1)
    df2=df2.reset_index()
    df3=df2
    df2=df2.drop("Date", axis=1)
    result=pd.concat([df, df2], axis=1, join='inner')
    results=result
    df3.to_csv(r'https://github.com/Utkarshhh20/trial/blob/main/trial.csv')
    results.to_csv(r'https://github.com/Utkarshhh20/trial/blob/main/trial2.csv')
    first_column1 = results.columns[0]
    results.to_csv('trial2.csv', index=False)
    #results = pd.read_csv('trial2.csv')
    # If you know the name of the column skip this
    # Delete first
    #result = result.drop([first_column], axis=1)
    # If you know the name of the column skip this
    first_column2 = df3.columns[0]
    # Delete first
    df3.to_csv('trial.csv', index=False)
    st.dataframe(result)
    st.dataframe(df3)
    csv_file = os.path.dirname(os.path.realpath(__file__)) + "/trial2.csv"
    vix_csv_file = os.path.dirname(os.path.realpath(__file__)) + "/trial.csv"

    spyVixDataFeed = SPYVIXData(dataname=csv_file)
    vixDataFeed = VIXData(dataname=vix_csv_file)
    start=start.split("-")
    end=end.split("-")
    for i in range(len(start)):
        start[i]=int(start[i])
    for j in range(len(end)):
        end[j]=int(end[j])
    year=end[0]-start[0]
    month=end[1]-start[1]
    day=end[2]-start[2]
    totalyear=year+(month/12)+(day/365)
    matplotlib.use('Agg')
    cerebro.adddata(spyVixDataFeed)
    cerebro.adddata(vixDataFeed)

    cerebro.addstrategy(VIXStrategy)

    cerebro.run()
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    final_value=cerebro.broker.getvalue()
    returns=(final_value-start_value)*100/start_value
    annual_return=returns/totalyear
    returns=round(returns, 2)
    annual_return=round(annual_return,2)
    returns=str(returns)
    annual_return=str(annual_return)
    figure = cerebro.plot(volume=False)[0][0]
    st.pyplot(figure)
    st.subheader(f"{ticker}'s total returns are {returns}% with a {annual_return}% APY")
    strategy=''

def backtestgolden():
    global strategy
    from goldencrossover import goldencrossover
    ticker=st.sidebar.text_input("Stock ticker", value="AAPL")
    start=st.sidebar.text_input("Start date", value="2018-01-31")
    end=st.sidebar.text_input("End date", value=today)
    cash=st.sidebar.text_input("Starting cash", value=10000)
    cash=int(cash)
    cerebro=bt.Cerebro()
    cerebro.broker.set_cash(cash)
    start_value=cash
    data = bt.feeds.PandasData(dataname=yf.download(ticker, start, end))
    start=start.split("-")
    end=end.split("-")
    for i in range(len(start)):
        start[i]=int(start[i])
    for j in range(len(end)):
        end[j]=int(end[j])
    year=end[0]-start[0]
    month=end[1]-start[1]
    day=end[2]-start[2]
    totalyear=year+(month/12)+(day/365)
    matplotlib.use('Agg')
    cerebro.adddata(data)

    cerebro.addstrategy(goldencrossover)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    final_value=cerebro.broker.getvalue()
    returns=(final_value-start_value)*100/start_value
    annual_return=returns/totalyear
    returns=round(returns, 2)
    annual_return=round(annual_return,2)
    returns=str(returns)
    annual_return=str(annual_return)
    figure = cerebro.plot()[0][0]
    st.pyplot(figure)
    st.subheader(f"{ticker}'s total returns are {returns}% with a {annual_return}% APY")
    strategy=''
def backtestbollinger():
    global strategy
    import numpy as np
    import pandas as pd
    import pandas_datareader as pdr
    import matplotlib.pyplot as plt
    symbol=st.sidebar.text_input("Stock ticker", value="AAPL")
    start=st.sidebar.text_input("Start date", value="2018-01-31")
    end=st.sidebar.text_input("End date", value=today)
    cash=st.sidebar.text_input("Starting cash", value=10000)
    cash=int(cash)
    def get_bollinger_bands(prices, rate=20):
        sma=prices.rolling(rate).mean()
        std = prices.rolling(rate).std()
        bollinger_up = sma + std * 2 # Calculate top band
        bollinger_down = sma - std * 2 # Calculate bottom band
        return bollinger_up, bollinger_down, sma
    df = pdr.DataReader(symbol, 'yahoo', start=start, end=end)
    start=start.split("-")
    end=end.split("-")
    for i in range(3):
        start[i]=int(start[i])
        end[i]=int(end[i])
    totalyear=(end[0]-start[0])+((end[1]-start[1])/12)+((end[2]-start[2])/365)
    df.index = np.arange(df.shape[0])
    closing_prices = df['Close']
    money=cash
    investpercent=0.9
    bollinger_up, bollinger_down, sma = get_bollinger_bands(closing_prices)
    matplotlib.use('Agg')
    fig=plt.title(symbol + ' Bollinger Bands')
    fig=plt.xlabel('Days')
    fig=plt.ylabel('Closing Prices')
    fig=plt.plot(sma, label='SMA', c='y', linewidth=1)
    fig=plt.plot(closing_prices, label='Closing Prices')
    fig=plt.plot(bollinger_up, label='Bollinger Up', c='g', linewidth=1)
    fig=plt.plot(bollinger_down, label='Bollinger Down', c='r', linewidth=1)
    sell=[]
    sellday=[]
    buy=[]
    buyday=[]
    close=df['Close']
    position=1
    for i in range(len(close)):
        if position==-1 and i==(len(close)-1):
            print('selling', df['Close'][i], bollinger_up[i])
            sell.append(df['Close'][i])
            sellday.append(i)
            position=1
        elif df['Close'][i]<=bollinger_down[i] and position==1:
            print('buying', df['Close'][i], bollinger_down[i])
            buy.append(df['Close'][i])
            buyday.append(i)
            position=-1
        elif df['Close'][i]>=bollinger_up[i] and position==-1:
            print('selling', df['Close'][i], bollinger_up[i])
            sell.append(df['Close'][i])
            sellday.append(i)
            position=1
    print(sell, buy)
    trades=len(buy)
    for i in range(trades):
        if cash==money:
            profit=((sell[i]-buy[i])/buy[i])*investpercent*cash
            cash=cash+profit
        else:
            profit=((sell[i]-buy[i])/buy[i])*investpercent*cash
            cash=cash+profit
    returns=(cash-money)*100/money
    annual_return=returns/totalyear
    returns=round(returns, 2)
    annual_return=round(annual_return,2)
    returns=str(returns)
    annual_return=str(annual_return)
    for i in range(len(sellday)):
        fig=plt.plot(sellday[i], sell[i], marker="v", markersize=7, markeredgecolor="red", markerfacecolor="red")
        fig=plt.plot(buyday[i], buy[i], marker="^", markersize=7, markeredgecolor="green", markerfacecolor="green")
    fig=plt.savefig(fname='hi')
    plt.legend()
    plt.show()
    st.pyplot(fig)
    st.subheader(f"{symbol}'s total returns are {returns}% with a {annual_return}% APY")
    strategy=''
def get_fundamentals():
    try:
        # Find fundamentals table
        fundamentals = pd.read_html(str(html), attrs = {'class': 'snapshot-table2'})[0]
        
        # Clean up fundamentals dataframe
        fundamentals.columns = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
        colOne = []
        colLength = len(fundamentals)
        for k in np.arange(0, colLength, 2):
            colOne.append(fundamentals[f'{k}'])
        attrs = pd.concat(colOne, ignore_index=True)
    
        colTwo = []
        colLength = len(fundamentals)
        for k in np.arange(1, colLength, 2):
            colTwo.append(fundamentals[f'{k}'])
        vals = pd.concat(colTwo, ignore_index=True)
        
        fundamentals = pd.DataFrame()
        fundamentals['Attributes'] = attrs
        fundamentals['Values'] = vals
        fundamentals = fundamentals.set_index('Attributes')
        return fundamentals

    except Exception as e:
        return e
    
def get_news():
    try:
        # Find news table
        news = pd.read_html(str(html), attrs = {'class': 'fullview-news-outer'})[0]
        links = []
        for a in html.find_all('a', class_="tab-link-news"):
            links.append(a['href'])
        
        # Clean up news dataframe
        news.columns = ['Date', 'News Headline']
        news['Article Link'] = links
        news = news.set_index('Date')
        return news

    except Exception as e:
        return e

def get_insider():
    try:
        # Find insider table
        insider = pd.read_html(str(html), attrs = {'class': 'body-table'})[0]
        
        # Clean up insider dataframe
        insider = insider.iloc[1:]
        insider.columns = ['Trader', 'Relationship', 'Date', 'Transaction', 'Cost', '# Shares', 'Value ($)', '# Shares Total', 'SEC Form 4']
        insider = insider[['Date', 'Trader', 'Relationship', 'Transaction', 'Cost', '# Shares', 'Value ($)', '# Shares Total', 'SEC Form 4']]
        insider = insider.set_index('Date')
        return insider

    except Exception as e:
        return e
title="""
    <style>
    .stockify {
    text-align: center;
    margin-top: -100px;
    margin-left: 67px;
    font-size: 40px;
    font-family: Arial, Helvetica, sans-serif;
    letter-spacing: 2px;
    }
    </style>
    <body>
    <p1 class='stockify'>Stockify</p1>
    </body>
    """
st.sidebar.markdown(title, unsafe_allow_html=True)
st.sidebar.write('_______________________')
title_alignment2="""
    <style>
    .trial2 {
    text-align: center;
    margin-top: -30px;
    margin-left: -13px;
    font-size: 300px;
    }
    </style>
    <body>
    <h1 class='trial2'>Select your dashboard</h1>
    </body>
    """
st.sidebar.markdown(title_alignment2, unsafe_allow_html=True)
dashboard = st.sidebar.selectbox('', ('Home', 'Screener', 'Fundamental Analysis', 'Technical Indicators', 'Backtesting', 'Pattern Stocks'), 0)
st.title(dashboard)
st.write('___')
if dashboard=='Home':
    st.header('Welcome to Stockify')
    title_alignment2='''
    <style>
    .trial {
    width: 55px;
    margin-top: -425px;
    margin-left: 130px;
    }
    </style>
    <body>
    <img src="https://img.icons8.com/nolan/344/home-page.png" alt="House" class='trial'></img>
    </body>
    '''
    image1='''
    <style>
    .stocks {
    width: 50px;
    margin-top: -165px;
    margin-left: 320px;
    }
    </style>
    <body>
    <img src="https://img.icons8.com/external-xnimrodx-lineal-gradient-xnimrodx/344/external-stock-economy-xnimrodx-lineal-gradient-xnimrodx.png" alt="House" class='stocks'></img>
    </body>'''
    #st.markdown(f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">', unsafe_allow_html=True,)
    st.markdown(title_alignment2, unsafe_allow_html=True)
    st.markdown(image1, unsafe_allow_html=True)
    st.subheader('What is stockify?')
    st.write('Stockify is a web application developed on python using the streamlit library which aims to provide you with the tools necessary to make trading and investing much simpler.\n ')
    st.write('''You can use this web app to do\n
1. Fundamental Analysis\n
2. Technical Analysis\n
3. Backtesting''')
   
if dashboard=='Pattern Stocks':
    @st.cache(suppress_st_warning=True)
    def data():
        st.subheader('Please wait while we fetch the data ⟳')
        with open('sp500.csv') as f:
            companies=f.read().splitlines()
            print(companies)
            for company in companies:
                symbol=company.split(',')[0]
                try: 
                    df=yf.download(symbol, start=start, end=today)
                    df.to_csv('sp500_daily/{}.csv'.format(symbol))
                except:
                    pass
    today=date.today()
    st.write(today)
    yesterday = today - timedelta(days=1)
    yesterday=f"{yesterday}"
    end=f"{today}"
    time=end.split('-')
    time[1]=int(time[1])
    time[1]=time[1]-1
    start=f"{time[0]}-{time[1]}-{time[2]}"
    lst=[]
    date_check=pd.read_csv('https://raw.githubusercontent.com/Utkarshhh20/trial2/main/sp500_daily/AAPL.csv')
    length=len(date_check)
    present=date_check['Date'][length-1]
    if yesterday!=present:
        data()
    df_sp500=pd.read_csv("sp500.csv")
    tickers=[]
    companynames=[]
    companies={}
    for i in df_sp500['Ticker']:
        tickers.append(i)
    for j in df_sp500['Name']:
        companynames.append(j)
    companies=dict(zip(tickers, companynames))
    for i in candlestick_patterns:
        lst.append(candlestick_patterns[i])
    pattern_name=st.sidebar.selectbox('Choose one of the following strategies',lst, 18)
    days=st.sidebar.text_input('Enter the days in which the pattern should occur', max_chars=3, value=1)
    days=int(days)
    for i in candlestick_patterns:
        if candlestick_patterns[i]==pattern_name:
            pattern=i
    datafiles=os.listdir('sp500_daily')
    for filename in datafiles:
        df=pd.read_csv('sp500_daily/{}'.format(filename))
        pattern_function= getattr(talib, pattern)
        try:
            result=pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
            last=result.tail(days).values[0]
            filename=filename.replace('.csv', '')
            stock=filename
            if last!=0:
                company_name=companies[stock]
                if last>0:
                    first,middle,last=st.columns([1.4,2.3,1])
                    first.subheader(f'{stock}')
                    middle.subheader(f'{company_name}')
                    last.subheader('BULLISH ⇪')
                    url=f"https://finviz.com/chart.ashx?t={stock}&ty=c&ta=1&p=d&s=l"
                    st.image(f"https://finviz.com/chart.ashx?t={stock}&ty=c&ta=1&p=d&s=l")
                    st.write('__________________________')
                elif last<0:
                    first,middle,last=st.columns([1.4,2.3,1])
                    first.subheader(filename)
                    middle.subheader(f'{company_name}')
                    last.subheader('BEARISH ⇩')
                    url=f"https://finviz.com/chart.ashx?t={stock}&ty=c&ta=1&p=d&s=l"
                    st.image(f"https://finviz.com/chart.ashx?t={stock}&ty=c&ta=1&p=d&s=l")
                    st.write('__________________________')
        except:
            pass
    
elif dashboard=='Fundamental Analysis':
    s_fundament = st.sidebar.selectbox('What would you like to do?', ('Learn', 'Check fundamentals'), 0)
    if s_fundament=='Learn':
        st.subheader('What Is Fundamental Analysis?')
        st.write('''• Fundamental analysis is a method of determining a stock's real or "fair market" value.\n
• Fundamental analysts search for stocks that are currently trading at prices that are higher or lower than their real value.\n
• If the fair market value is higher than the market price, the stock is deemed to be undervalued and a buy recommendation is given.\n
• In contrast, technical analysts ignore the fundamentals in favor of studying the historical price trends of the stock.\n''')
        st.subheader('Understanding Fundamental Analysis')
        st.write('''All stock analysis tries to determine whether a security is correctly valued within the broader market. Fundamental analysis is usually done from a macro to micro perspective in order to identify securities that are not correctly priced by the market.\n
For stocks, fundamental analysis uses revenues, earnings, future growth, return on equity, profit margins, and other data to determine a company's underlying value and potential for future growth. All of this data is available in a company's financial statements.\n''')
        st.subheader('Financial Statements: Quantitative Fundamentals to Consider')
        st.write('Financial statements are the medium by which a company discloses information concerning its financial performance. Followers of fundamental analysis use quantitative information gleaned from financial statements to make investment decisions. The three most important financial statements are income statements, balance sheets, and cash flow statements.')
        st.write('')
        st.write('''**Check the fundamentals of any stock by entering the ticker in the sidebar on the next page.**\n''')
    elif s_fundament=='Check fundamentals':
        symbol=st.sidebar.text_input("Ticker", value='AAPL', max_chars=10)
        pd.set_option('display.max_colwidth', 25)
        st.subheader(f"{symbol}'s Fundamentals ")
        # Set up scraper
        url = ("https://finviz.com/quote.ashx?t=" + symbol.lower())
        req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})
        webpage = urlopen(req)
        html = bs(webpage, "html.parser")
        fundament=get_fundamentals()
        inside=get_insider()
        news=get_news()
        st.write(fundament)
        st.write('Several important indicators which could be used like marketcap, P/E, PEG, Debt/Eq, ROI etc have been indicated within the dataframe above. These can be used to find entry and exit positions and see if the company is fundamentally sound.')
        st.write('_______________________________________________________________________________________________')
        st.subheader("\n\nRecent trades made by company's officials")
        st.write(inside)
        st.write('**When Insiders Buy, Should Investors Join Them?**\n \n')
        st.write('''This question doesn't have any right answers but one could sure speculate based on this information.\n
Tips for beating the market tend to come and go quickly, but one has held up extremely well: if executives, directors, or others with inside knowledge of a public company are buying or selling shares, investors should consider doing the same thing. Research shows that insider trading activity is a valuable barometer of broad shifts in market and sector sentiment.
However, before chasing each insider move, outsiders need to consider the factors that dictate the timing of trades and the factors that conceal the motivations and also that information is made public after a delay of the transaction made.''')
        st.write('_______________________________________________________________________________________________')
        st.subheader(f'Recent news on {symbol} stock')
        st.write(news)
        st.write('')
        st.write("\nStocks correlate the performance with the current market conditions and business news. They also predict the performance of the stock market and advise on buying and selling of stocks, mutual funds, and other securities.")
if dashboard=='Backtesting':
    strategy = st.sidebar.selectbox("Which Strategy?", ('Intro', 'RSI', 'Volatility', 'Golden Crossover', 'Bollinger Bands'), 0, key='strategy')
    st.header(strategy)
    if strategy=='Intro':
        st.subheader('What is backtesting?')
        st.write('''• Backtesting assesses the viability of a trading strategy or pricing model by discovering how it would have played out retrospectively using historical data.\n
• The underlying theory is that any strategy that worked well in the past is likely to work well in the future, and conversely, any strategy that performed poorly in the past is likely to perform poorly in the future.\n
• When testing an idea on historical data, it is beneficial to reserve a time period of historical data for testing purposes. If it is successful, testing it on alternate time periods or out-of-sample data can help confirm its potential viability.''')
        st.subheader('What is the need for backtesting?')
        st.write('Backtesting is one of the most important aspects of developing a trading system. If created and interpreted properly, it can help traders optimize and improve their strategies, find any technical or theoretical flaws, as well as gain confidence in their strategy before applying it to the real world markets.')
        st.subheader('Please choose one of our strategies on the sidebar to backtest')
    while strategy=='RSI':
            backtestrsi()
    while strategy=='Volatility':
        volatility()
    while strategy=='Golden Crossover':
            backtestgolden()
    while strategy=='Bollinger Bands':
            backtestbollinger()
st.write('hi')
df = pdr.DataReader('AAPL', 'yahoo', start='2014-01-01', end='2017-01-01')
st.dataframe(df)
x=df['Close']
matplotlib.use('Agg')
fig=plt.title('AAPL' + ' Bollinger Bands')
fig=plt.xlabel('Days')
fig=plt.ylabel('Closing Prices')
fig=plt.plot(x, label='Closing Prices')
fig=plt.savefig(fname='hi')
st.pyplot(fig)
