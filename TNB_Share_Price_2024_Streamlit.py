#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st


import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, time
import time as t
import clipboard
import pandas as pd
import random 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

 
gifs = ["giphy.gif", "ysb.gif", "smol-illegally-smol-cat.gif", 
"cool-fun.gif", "mcdo-cat-meme.gif", "unhand-me-wiggle-cat.gif",
"quit.gif", "shocked-shocked-cat.gif", "santa-christmas.gif",
"fat-cat-laser-eyes.gif"]

n=random.randint(0,len(gifs)-1) 

if st.button('Calculate share price'):
    #VIDEO_URL = "https://tenor.com/view/cat-zoning-out-cat-stare-black-cat-black-cat-tiktok-stare-gif-6568742496074847242"
    st.image(gifs[n])
    with st.status("Compiling info...", expanded=True) as status:
        if 'key' in st.session_state:
            del st.session_state.key

        if 'key1' in st.session_state:
            del st.session_state.key1
        
        st.write(f"Loading data from TNB wesbite...")
        start_time = t.time()


        # enable headless mode in Selenium
        options = Options()
        # Chrome 104 Android User Agent
        custom_user_agent = "Mozilla/5.0 (Linux; Android 11; 100011886A Build/RP1A.200720.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.69 Safari/537.36"
        options.add_argument(f'user-agent={custom_user_agent}')
        options.add_argument('--headless')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
            options=options)


        url = "https://www.insage.com.my/ir/tenaga/priceticker.aspx"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
        data = requests.get(url, verify=False, headers=headers).text
        soup = BeautifulSoup(data, 'html.parser')

        # Creating list with all tables
        tables = soup.find_all('table')

        #  Looking for the table with the classes 'wikitable' and 'sortable'
        TNB_share_price_curr = soup.find('table', class_='table table-hover mt10')
        TNB_curr_price = float(TNB_share_price_curr.tbody.find_all('td')[2].text.strip())


        TNB_share_price_prev = soup.find('div', class_='col-sm-6 pt10')
        TNB_prev_price = float(TNB_share_price_prev.find_all('th')[0].text.strip())

        TNB_volume = soup.find('div', class_='col-sm-6 mt10')
        current_volume = TNB_volume.tbody.find_all('th')[0].text.strip()
        current_volume = int(current_volume.replace(',', ''))/(10**6)



        # visit your target site
        driver.get('https://www.investing.com/indices/ftse-malaysia-klci')

        # release the resources allocated by Selenium and shut down the browser
        KLCI_curr_price = driver.find_element(By.CSS_SELECTOR, "[data-test='instrument-price-last']").text
        KLCI_curr_price = float(KLCI_curr_price.replace(',', ''))

        st.write("Getting KLCI index... it's only been %s seconds..." % round(t.time() - start_time, 0))
        start_time1 = t.time()
        

        KLCI_prev_price = driver.find_element(By.CSS_SELECTOR, "[data-test='prevClose']").text
        KLCI_prev_price = float(KLCI_prev_price.replace(',', ''))

        st.write("Getting MSCI index... it only took %s seconds..." % round(t.time() - start_time1, 0))

        start_time1 = t.time()

        driver.get('https://www.investing.com/indices/msci-ac-asia-pacific-historical-data')
        MSCI_curr_price =  driver.find_element(By.CSS_SELECTOR, "[data-test='instrument-price-last']").text
        MSCI_curr_price = float(MSCI_curr_price.replace(',', ''))


        driver.get('https://www.investing.com/indices/msci-ac-asia-pacific')
        delay = 3 # seconds
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='prevClose']")))
        MSCI_prev_price = driver.find_element(By.CSS_SELECTOR, "[data-test='prevClose']").text
        MSCI_prev_price = float(MSCI_prev_price.replace(',', ''))

        driver.quit()

        st.write("Compiling and calculating data... it only took %s seconds..." % round(t.time() - start_time1, 0))
        start_time1 = t.time()

        # Displays Time

        current_time = datetime.now().strftime(format = '%d-%b-%Y %I:%M %p')

        text_summary = (f'Share Price as of: {current_time}\n' 
            f'TNB Share Price: {TNB_curr_price}\n' 
            f'TNB Volume: {str(current_volume)+" mn"}\n'
            f'KLCI: {KLCI_curr_price}\n'
            f'MSCI: {MSCI_curr_price}\n')


        def str_to_float(string, decimal):
            decimal = '.'+str(decimal)+'f'

            return(format(float(string), decimal))

        def float_signs(string, symbol, dp=2):
            dp = '.'+str(dp)+'f'

            if symbol == "RM": 
                if float(string) < 0: 
                    return("-RM"+format(abs(string), dp))
                elif float(string) > 0:
                    return("+RM"+format(string, dp))
                return("RM"+format(string, dp))
            elif symbol == "%": 
                string = string * 100
                if float(string) < 0:
                    text = '{:-'+dp+'}%'
                    return(text.format(string))
                elif float(string) > 0:
                    text = '{:+'+dp+'}%'
                    return(text.format(string))
                text = '{:'+dp+'}%'
                return(text.format(string))

        TNB_NOSH = 5787331871/10**9
        TNB_market_cap = TNB_NOSH * TNB_curr_price
        TNB_market_cap_prev = TNB_NOSH * TNB_prev_price
        KNB_Number_of_Shares = 1245620404 # As of 2 April 2024 divestment
        KNB_Share = (KNB_Number_of_Shares/(TNB_NOSH*10**9))/100
        KNB_market_cap_since = 9.98*5.733331871
        TNB_Share_Price_Start_Year = 9.98 # as of2/1/2024
        K_Dividend = 0.61095409772 # RM'bn, as of 2023, to be renewed for 2024
        Gain_in_K_stake = (TNB_curr_price -TNB_Share_Price_Start_Year)*(KNB_Number_of_Shares/10**9)
        Gain_in_K_stake_inc_div = Gain_in_K_stake + K_Dividend
        KNB_Share_Absolute = 100*(TNB_market_cap*KNB_Share-TNB_market_cap_prev*KNB_Share) # Change in market share from prev close
        K_Div_yield = ((K_Dividend*10**9)/(1305620404))/TNB_curr_price # Divided by pre-divestment number of shares since ex-date was before divestment

        since_date = '2 Jan 2024'


        def is_time_between(begin_time, end_time, check_time=None):
            # If check time is not given, default to current UTC time
            check_time = check_time or datetime.now().time()
            if begin_time < end_time:
                return check_time >= begin_time and check_time <= end_time
            else: # crosses midnight
                return check_time >= begin_time or check_time <= end_time

        if is_time_between(time(0,0), time(14,0)): 
            time_of_day = "*TNB 1st Half Update - Noon Close -"

        if is_time_between(time(14,0), time(23,59)): 
            time_of_day = "*TNB 2nd Half Update - Day Close -"

        text = (
            f"{time_of_day} {datetime.now().strftime(format = '%d/%m/%Y')}*\n"
            f"*Price:* RM{format(TNB_curr_price, '.2f')}\n"
            f"*Prev Close (day):* RM{format(TNB_prev_price, '.2f')}\n"
            f"({float_signs(TNB_curr_price-TNB_prev_price, 'RM')}; {float_signs((TNB_curr_price/TNB_prev_price)-1, '%')})\n"
            f"*Market Cap:* RM{format(TNB_market_cap, '.1f')}bn\n"
            f"*Khazanah's Share:* RM{format(KNB_Share*TNB_market_cap*100, '.1f')}bn\n"
            f"({float_signs(KNB_Share_Absolute, 'RM')}; {float_signs((TNB_curr_price/TNB_prev_price)-1, '%')})\n"
            f"*Volume:* {format(current_volume, '.2f')}m\n"
            f"*KLCI Index:* {format(KLCI_curr_price, '.2f')} ({float_signs(KLCI_curr_price/KLCI_prev_price-1, '%')})\n"
            f"*MSCI AC Asia Index:* {format(MSCI_curr_price, '.2f')} ({float_signs(MSCI_curr_price/MSCI_prev_price-1, '%')})\n\n"
            f"*Khazanah gain/loss since yesterday's market close:*\n"
            f"{float_signs(KNB_Share_Absolute*1000, 'RM',1)}m\n\n"
            f"*Since {since_date}:*\n"
            f"*TNB Mkt Cap increase/decrease:*\n"
            f"RM{format(TNB_market_cap-KNB_market_cap_since, '.2f')}bn (RM{format(TNB_market_cap, '.2f')}bn vs RM{format(KNB_market_cap_since, '.2f')}bn)\n"
            f"*KNB Stake increase/decrease incl. Dividends:*\n"
            f"RM{format(Gain_in_K_stake_inc_div, '.2f')}bn\n"
            f"*Gain/Loss in Khazanah Stake:*\n"
            f"RM{format(Gain_in_K_stake, '.2f')}bn\n"
            f"*Dividends received (TTM):* RM{format(K_Dividend*10**3, '.1f')}m\n"
            f"*Dividend yield (TTM):* {format(100*K_Div_yield, '.2f')}%\n"

            )
        st.session_state.key = text
        st.session_state.key1 = text_summary
        
        st.write("Saving my work into Excel... it only took %s seconds..." % round(t.time() - start_time1, 0))
        start_time1 = t.time()
        df = pd.read_csv(r"TNB_Share_Price_2024_Streamlit.csv")
        #df = pd.DataFrame(columns=['Date','TNB_Share_Price_Day', 'TNB_Volume_Day', 'KLCI_Day', 'MSCI_Day',
                                #'TNB_Share_Price_Close', 'TNB_Volume_Close', 'KLCI_Close', 'MSCI_Close'])

        today_date = datetime.now().strftime(format = '%A')
        if (today_date != 'Saturday') and (today_date != 'Sunday') and (is_time_between(time(0,0), time(13,30))): 
            if not (df == datetime.now().strftime(format = '%#d/%#m/%Y')).any().any():
                info  = {'Date':datetime.now().strftime(format = '%#d/%#m/%Y'), 
                        'TNB_Share_Price_Day':TNB_curr_price, 
                        'TNB_Volume_Day':current_volume,
                        'KLCI_Day':KLCI_curr_price,
                        'MSCI_Day':MSCI_curr_price}
                df = pd.concat([df, pd.DataFrame(info, index=[0])], ignore_index=True)

        if (today_date != 'Saturday') and (today_date != 'Sunday') and (is_time_between(time(14,0), time(23,59))):
            if pd.isnull(df.loc[df[df['Date'] == datetime.now().strftime(format = '%#d/%#m/%Y')].index[0], "TNB_Share_Price_Close"]):
                df.loc[df['Date'] == datetime.now().strftime(format = '%#d/%#m/%Y'), 'TNB_Share_Price_Close'] = TNB_curr_price
                df.loc[df['Date'] == datetime.now().strftime(format = '%#d/%#m/%Y'), 'TNB_Volume_Close'] = current_volume
                df.loc[df['Date'] == datetime.now().strftime(format = '%#d/%#m/%Y'), 'KLCI_Close'] = KLCI_curr_price
                df.loc[df['Date'] == datetime.now().strftime(format = '%#d/%#m/%Y'), 'MSCI_Close'] = MSCI_curr_price

        df.to_csv("TNB_Share_Price_2024_Streamlit.csv", index=False)
        
        st.write("Done! Only took %s seconds..." % round(t.time() - start_time, 0))

        if 'key' not in st.session_state:
            text = text
            st.session_state['key'] = text

        clipboard.copy(text)
        st.balloons()
        st.toast(f"Copied to clipboard: {text}", icon='✅' )
    st.code(text_summary)
    st.code(text)


if st.button("Copy to WhatsApp 📋"): 
    try:
        clipboard.copy(st.session_state.key)
        st.toast(f"Copied to clipboard: {st.session_state.key}", icon='✅' )
        st.code(st.session_state.key1)
        st.code(st.session_state.key)
    except AttributeError: 
        st.write("Press calculate share price first!")
    
