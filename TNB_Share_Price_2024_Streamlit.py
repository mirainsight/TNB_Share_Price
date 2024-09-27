#!/usr/bin/env python
# coding: utf-8

# In[1]:

# import relevant libraries
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, time
import time as t
import pandas as pd
import random 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import st_copy_to_clipboard
from st_copy_to_clipboard import st_copy_to_clipboard
from pytz import timezone
import pytz
import github
from github import Github
from pandas.tseries.offsets import BDay

disable_warnings(InsecureRequestWarning)

def change_param():
    st.write("hi")

def update_data():
    st.write("yo")

# UPDATE NUMBERS HERE! 
hardcoded_var = {
    "TNB_NOSH" : 5812948071/10**9, # Updated as of 10th July 2024
    "KNB_Number_of_Shares" : 1215620404, # As of 19 June 2024 divestment
    "TNB_Share_Price_Start_Year" : 9.98, # As of 2/1/2024
    "since_date" : '2 Jan 2024',
    "K_Dividend" : 0.61030538584 + 0, # Received TTM RM'bn, as of 18/4/24, updated for recent div date 
    # Note: "202x dividend" is the amount of dividend received in 202x, not the declared amount
}

# set up page
st.set_page_config(page_title = "TNB Updates", page_icon="⚡") # sets
repo_owner = 'mirainsight'
repo_name = 'TNB_Share_Price'
file_path = 'TNB_Share_Price_2024_Streamlit.csv'
token = st.secrets['Github_token']
github = Github(token)
repo = github.get_user(repo_owner).get_repo(repo_name)
content = repo.get_contents(file_path)

# cute cat gifs
gifs = ["giphy.gif", "ysb.gif", "smol-illegally-smol-cat.gif", 
"cool-fun.gif", "mcdo-cat-meme.gif", "unhand-me-wiggle-cat.gif",
"quit.gif", "shocked-shocked-cat.gif", "santa-christmas.gif",
"fat-cat-laser-eyes.gif"]

n=random.randint(0,len(gifs)-1) # randomizes the gifs that appear

start = st.button('Calculate share price') # button to press

def calculate(start, variables=hardcoded_var):
    if start:
        st.image(gifs[n]) # sets the gifs
        
        #
        with st.status("Compiling info...", expanded=True) as status:
            if 'key' in st.session_state:
                del st.session_state.key
        
            if 'key1' in st.session_state:
                del st.session_state.key1
                              
            progress_text = "TNB share price calculator loading. Please wait."
            #my_bar = st.progress(0, text=progress_text)
            st.write(f"Loading data from TNB wesbite...")
            start_time = t.time()
        
            # Set up web-scraping
            
            # enable headless mode in Selenium
            options = Options()
            
            # Chrome 104 Android User Agent
            custom_user_agent = "Mozilla/5.0 (Linux; Android 11; 100011886A Build/RP1A.200720.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.69 Safari/537.36"
            options.add_argument(f'user-agent={custom_user_agent}')
            options.add_argument('--headless')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument("--start-maximized")
            options.add_argument("--window-size=1920x1080") #I added this
         
            service = Service()
            driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
                ),
                options=options,
            )
                 
            st.write("Getting TNB data... it's only been %s seconds..." % round(t.time() - start_time, 0))
            start_time1 = t.time()    
            
            driver.get('https://www.investing.com/equities/tenaga-nasional-bhd')
            wait_time = 1
            error = True 
            iteration = 1
            while error:
                st.write(f"Iteration {iteration} of 1")

                try:
                    WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='instrument-price-last']"))).click()
                    error = False
                    st.write(f"Success during iteration {iteration}")
                except: 
                    wait_time += 1
                    iteration += 1
                
            TNB_share_price_curr = driver.find_element(By.CSS_SELECTOR, "[data-test='instrument-price-last']").text                                                      
            TNB_curr_price = float(TNB_share_price_curr)
        
            TNB_share_price_prev = driver.find_element(By.CSS_SELECTOR, "[data-test='prevClose']").text
        
            try:
                TNB_prev_price = float(TNB_share_price_prev)
            except ValueError:
                TNB_prev_price = TNB_share_price_prev
        
            TNB_volume = driver.find_element(By.CSS_SELECTOR, "[data-test='volume']").text
            current_volume = TNB_volume.replace(',', '')
            current_volume = (float(current_volume))/(10**6)
        
            st.write("Getting KLCI index... it's only been %s seconds..." % round(t.time() - start_time1, 0))
            start_time1 = t.time()
        
            # visit your target site
            driver.get('https://www.investing.com/indices/ftse-malaysia-klci')
        
            # release the resources allocated by Selenium and shut down the browser
            KLCI_curr_price = driver.find_element(By.CSS_SELECTOR, "[data-test='instrument-price-last']").text
            KLCI_curr_price = float(KLCI_curr_price.replace(',', ''))
        
        
            KLCI_prev_price = driver.find_element(By.CSS_SELECTOR, "[data-test='prevClose']").text
            KLCI_prev_price = float(KLCI_prev_price.replace(',', ''))
        
            st.write("Getting MSCI index... it only took %s seconds..." % round(t.time() - start_time1, 0))
        
            start_time1 = t.time()
        
            driver.get('https://www.investing.com/indices/msci-ac-asia-pacific-historical-data')
            MSCI_curr_price =  driver.find_element(By.CSS_SELECTOR, "[data-test='instrument-price-last']").text
            MSCI_curr_price = float(MSCI_curr_price.replace(',', ''))
        
        
            driver.get('https://www.investing.com/indices/msci-ac-asia-pacific')
            delay = 20 # seconds
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='prevClose']")))
            MSCI_prev_price = driver.find_element(By.CSS_SELECTOR, "[data-test='prevClose']").text
            MSCI_prev_price = float(MSCI_prev_price.replace(',', ''))
        
            driver.quit()
        
            st.write("Compiling and calculating data... it only took %s seconds..." % round(t.time() - start_time1, 0))
            start_time1 = t.time()
        
            # Displays Time
        
            current_time = datetime.now(timezone('Asia/Singapore')).strftime(format = '%d-%b-%Y %I:%m %p')
        
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
        
            # Set up of formularised variables
            TNB_NOSH = variables["TNB_NOSH"]
            KNB_Number_of_Shares = variables["KNB_Number_of_Shares"]
            TNB_Share_Price_Start_Year = variables["TNB_Share_Price_Start_Year"]
            KNB_market_cap_since = TNB_Share_Price_Start_Year * TNB_NOSH
            K_Dividend = variables["K_Dividend"]
            since_date = variables["since_date"]
            
            TNB_market_cap = TNB_NOSH * TNB_curr_price
            TNB_market_cap_prev = TNB_NOSH * TNB_prev_price
            KNB_NOSH_formatted = str('{:,}'.format(KNB_Number_of_Shares)) 
            KNB_Share = (KNB_Number_of_Shares/(TNB_NOSH*10**9))/100
            KNB_Stake = KNB_Number_of_Shares/(TNB_NOSH*(10**9))
            Gain_in_K_stake = (TNB_curr_price -TNB_Share_Price_Start_Year)*(KNB_Number_of_Shares/10**9)
            Gain_in_K_stake_inc_div = Gain_in_K_stake + K_Dividend
            KNB_Share_Absolute = 100*(TNB_market_cap*KNB_Share-TNB_market_cap_prev*KNB_Share) # Change in market share from prev close
            K_Div_yield = ((K_Dividend*10**9)/(KNB_Number_of_Shares))/TNB_curr_price # Divided by pre-divestment number of shares since ex-date was before divestment        
        
            def is_time_between(begin_time, end_time, check_time=None):
                # If check time is not given, default to current UTC time
                check_time = check_time or datetime.now(timezone('Asia/Singapore')).time()
                if begin_time < end_time:
                    return check_time >= begin_time and check_time <= end_time
                else: # crosses midnight
                    return check_time >= begin_time or check_time <= end_time
        
            if is_time_between(time(0,0, tzinfo=pytz.timezone('Asia/Singapore')), time(14,0, tzinfo=pytz.timezone('Asia/Singapore'))): 
                time_of_day = "*TNB 1st Half Update - Noon Close -"
        
            if is_time_between(time(14,0), time(23,59)): 
                time_of_day = "*TNB 2nd Half Update - Day Close -"
        
            text = (
                f"{time_of_day} {datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%m/%Y')}*\n"
                f"*Price:* RM{format(TNB_curr_price, '.2f')}\n({float_signs((TNB_curr_price/TNB_Share_Price_Start_Year)-1, '%')} YTD)\n"
                f"*Prev Close (day):* RM{format(TNB_prev_price, '.2f')}\n"
                f"({float_signs(TNB_curr_price-TNB_prev_price, 'RM')}; {float_signs((TNB_curr_price/TNB_prev_price)-1, '%')})\n"
                f"*Market Cap:* RM{format(TNB_market_cap, '.1f')}bn\n"
                f"*Khazanah's Share:* RM{format(KNB_Share*TNB_market_cap*100, '.1f')}bn\n"
                f"({float_signs(KNB_Share_Absolute, 'RM')}bn; {float_signs((TNB_curr_price/TNB_prev_price)-1, '%')})\n"
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
                f"*KNB Stake*: {KNB_NOSH_formatted} ({format(100*KNB_Stake, '.2f')}%)"
                )
            st.session_state.key = text
            st.session_state.key1 = text_summary
            
            st.write("Saving my work into Excel... it only took %s seconds..." % round(t.time() - start_time1, 0))
            start_time1 = t.time()
            df = pd.read_csv(r"TNB_Share_Price_2024_Streamlit.csv")
            #df = pd.DataFrame(columns=['Date','TNB_Share_Price_Day', 'TNB_Volume_Day', 'KLCI_Day', 'MSCI_Day',
                                    #'TNB_Share_Price_Close', 'TNB_Volume_Close', 'KLCI_Close', 'MSCI_Close'])
        
            today_date = datetime.now(timezone('Asia/Singapore')).strftime(format = '%A')
            yesterday_date = datetime.now(timezone('Asia/Singapore')) - BDay(4)
            if (today_date != 'Saturday') and (today_date != 'Sunday') and (is_time_between(time(12, 30, tzinfo=pytz.timezone('Asia/Singapore')), time(13,00, tzinfo=pytz.timezone('Asia/Singapore')))):
                st.header("⚠️ Website needs more time to be updated. Please try again at 1pm for most accurate data ⚠️")
                
            if (today_date != 'Saturday') and (today_date != 'Sunday') and (is_time_between(time(17, 0, tzinfo=pytz.timezone('Asia/Singapore')), time(18,0, tzinfo=pytz.timezone('Asia/Singapore')))):
                st.header("⚠️ Website needs more time to be updated. Please try again at 6pm for most accurate data ⚠️")
                
            if (today_date != 'Saturday') and (today_date != 'Sunday') and (is_time_between(time(12, 30, tzinfo=pytz.timezone('Asia/Singapore')), time(14,00, tzinfo=pytz.timezone('Asia/Singapore')))):
                if pd.isnull(df.loc[df.index[df['Date'] == yesterday_date.strftime(format = '%d/%-m/%Y')].tolist()[0], "TNB_Share_Price_Close"]):
                    df.loc[df['Date'] == datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y'), 'TNB_Share_Price_Close'] = TNB_share_price_prev
                    #df.loc[df['Date'] == datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y'), 'TNB_Volume_Close'] = current_volume
                    df.loc[df['Date'] == datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y'), 'KLCI_Close'] = KLCI_prev_price
                    df.loc[df['Date'] == datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y'), 'MSCI_Close'] = MSCI_prev_price
                elif not (df == datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y')).any().any():
                    info  = {'Date':datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y'), 
                            'TNB_Share_Price_Day':TNB_curr_price, 
                            'TNB_Volume_Day':current_volume,
                            'KLCI_Day':KLCI_curr_price,
                            'MSCI_Day':MSCI_curr_price}
                    df = pd.concat([df, pd.DataFrame(info, index=[0])], ignore_index=True)
        
            if (today_date != 'Saturday') and (today_date != 'Sunday') and (is_time_between(time(17,0, tzinfo=pytz.timezone('Asia/Singapore')), time(23,59, tzinfo=pytz.timezone('Asia/Singapore')))):
                 if pd.isnull(df.loc[df.index[df['Date'] == datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y')].tolist()[0], "TNB_Share_Price_Close"]):
                    df.loc[df['Date'] == datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y'), 'TNB_Share_Price_Close'] = TNB_curr_price
                    df.loc[df['Date'] == datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y'), 'TNB_Volume_Close'] = current_volume
                    df.loc[df['Date'] == datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y'), 'KLCI_Close'] = KLCI_curr_price
                    df.loc[df['Date'] == datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y'), 'MSCI_Close'] = MSCI_curr_price
        
            df.to_csv("TNB_Share_Price_2024_Streamlit.csv", index=False)
            with open('TNB_Share_Price_2024_Streamlit.csv', 'rb') as f:
                contents = f.read()
            commit_message = f"Update CSV file as of {datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y')}"
            repo.update_file(file_path, commit_message, contents, content.sha)
            
            st.write("Done! Only took %s seconds..." % round(t.time() - start_time, 0))
        
            if 'key' not in st.session_state:
                st.session_state['key'] = text
                st.session_state.key1 = text_summary
        
            st.balloons()
            st.toast(f"Done calculation!: {text}", icon='✅' )
            st_copy_to_clipboard(text)
            # st.text_area("Key stats summary", text_summary)
            st.code(text)

calculate(start)

page_names_to_funcs = {
    "Share Price (Default)": calculate,
    "Change Parameters": change_param,
    "Missed updating?": update_data
}
demo_name = st.sidebar.selectbox("Share Price Calculator", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()

if st.button("Show again"): 
    try:
        # st_copy_to_clipboard('test')
        # st_copy_to_clipboard(st.session_state.key)
        st.toast(f"Done calculation!: {st.session_state.key}", icon='✅' )
        # st.text_area("Key stats summary", st.session_state.key1)
        st.code(st.session_state.key)
    except AttributeError: 
        st.write("Press calculate share price first!")
    
