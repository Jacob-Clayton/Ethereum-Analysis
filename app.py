#Import libraries and env for API key
from requests import get
from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
from dotenv import load_dotenv
import os 
import json

#Etherscan api url
BASE_URL = 'https://api.etherscan.io/api'

#Formula to convert eth value into recognisable eth value
ETH_VALUE = 10 ** 18

#Function to configure the .env with the api key
def configure():
    load_dotenv()

#Streamlit App setup
st.title('Ethereum Balance App')
st.markdown('###### A web app to visualise the historical Ethereum balance of any Ethereum address')

#Streamlit text entry box for eth address
address = st.text_input("Enter Ethereum Address: ")

#Function to call the api
def make_api_url(module, action, address, **kwargs):
    #Call the api key function
    configure()
    url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={os.getenv('API_KEY')}"

    for key, value in kwargs.items():
        url += f"&{key}={value}"
    return url
    
    

#Funtion to get account balance
def get_account_balance(address):
    balance_url = make_api_url("account", "balance", address, tag='latest')
    response = get(balance_url)
    data = response.json()

    #Formula to convert resulting number into recognisable Eth value
    value = int(data['result'])/ ETH_VALUE
    return value


#Function to get a list of all transactions by address
def get_transactions(address):

    #Get external eth transactions
    transactions_url = make_api_url('account', 'txlist', address, startblock=0, endblock=99999999, page=1, offset=10000, sort='asc')
    response = get(transactions_url)
    data = json.loads(response.text)['result']


    #Get internal eth transactions
    internal_tx_url = make_api_url('account', 'txlistinternal', address, startblock=0, endblock=99999999, page=1, offset=10000, sort='asc',)
    response2 = get(internal_tx_url)
    data2 = json.loads(response2.text)['result']

    #Merge external and internal eth transactions
    data.extend(data2)

    #Sort transactions by date
    data.sort(key=lambda x: int(x['timeStamp']))
    current_balance = 0
    balances = []
    times = []

    #Calculate value of ETH transferred externally and internally
    for tx in data:
        to = tx['to']
        value = int(tx['value'])/ETH_VALUE

        #Calculate ETH spent on gas
        if 'gasPrice' in tx:
            gas = int(tx['gasUsed']) * int(tx['gasPrice']) / ETH_VALUE
        else:
            gas = int(tx['gasUsed']) / ETH_VALUE
            
        time = datetime.fromtimestamp(int(tx['timeStamp']))
        money_in = to.lower() == address.lower()

        #Get ETH balance over time of the address
        if tx['isError'] == '0':
            if money_in:
                current_balance += value
            else:
                current_balance -= value + gas

        balances.append(current_balance)
        times.append(time)

    #print(current_balance)   

    # Calculate max, min, and average balance
    max_balance = max(balances)
    min_balance = min(balances)
    avg_balance = sum(balances) / len(balances)   

    # Find the index of the max and min balance values
    max_index = balances.index(max_balance)
    min_index = balances.index(min_balance)

    # Get the date of the max and min balance values
    max_date = times[max_index]
    min_date = times[min_index]

    # Format the date values
    max_date = max_date.strftime("%d %B %Y")
    min_date = min_date.strftime("%d %B %Y")

    # Calculate the date of the first and last transactions
    first_date = times[0]
    last_date = times[-1]

    # Calculate the number of days between the first and last transactions
    num_days = (last_date - first_date).days

    #Create matplotlib chart on streamlit
    st.set_option('deprecation.showPyplotGlobalUse', False)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(times, balances)
    plt.ylabel('Ethereum')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%y'))

    # Display max, min, and average balance on the page
    st.markdown("Max balance: %.4f ETH on %s" % (max_balance, max_date))
    st.markdown("Min balance: %.4f ETH on %s" % (min_balance, min_date))
    st.markdown("Average balance: %.4f ETH over %d days" % (avg_balance, num_days))

#Call function, comment out for final version because it is called later
#get_transactions(address)

#Create matplotlib chart on streamlit when an address is entered
if address:
    st.pyplot(get_transactions(address))
    st.text('Chart for: ') 
    st.text(address)    

