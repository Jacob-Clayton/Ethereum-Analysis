#Import library and API key
from etherscan import Etherscan
from requests import get
from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
from dotenv import load_dotenv
import os 

BASE_URL = 'https://api.etherscan.io/api'
API_KEY = os.getenv('API_KEY')
ETH_VALUE = 10 ** 18
#address = '0x364636B067d899B53d9e524Fa74305c90DCb7717'

def configure():
    load_dotenv()

#Streamlit App setup

st.title('Ethereum Wallet Balance App')
st.markdown('###### A web app to visualise the historical Ethereum balance of any Ethereum wallet')

address = st.text_input("Enter Ethereum Wallet Address: ")


#Function to call the api endpoint
def make_api_url(module, action, address, **kwargs):
    configure()
    url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={API_KEY}"

    for key, value in kwargs.items():
        url += f"&{key}={value}"
    return url

#Funtion to get account balance
def get_account_balance(address):
    balance_url = make_api_url("account", "balance", address, tag='latest')
    response = get(balance_url)
    data = response.json()

    value = int(data['result'])/ ETH_VALUE
    return value

#Function to get a list of all transactions by address
def get_transactions(address):

    #Get external eth transactions
    transactions_url = make_api_url('account', 'txlist', address, startblock=0, endblock=99999999, page=1, offset=10000, sort='asc')
    response = get(transactions_url)
    data = response.json()['result']

    #Get internal eth transactions
    internal_tx_url = make_api_url('account', 'txlistinternal', address, startblock=0, endblock=99999999, page=1, offset=10000, sort='asc')
    response2 = get(internal_tx_url)
    data2 = response2.json()['result']

    data.extend(data2)
    data.sort(key=lambda x: int(x['timeStamp']))

    current_balance = 0
    balances = []
    times = []

    #Calculate value of ETH transferred externally and internally
    for tx in data:
        to = tx['to']
        from_addr = tx['from']
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

    #Create matplotlib chart
    st.set_option('deprecation.showPyplotGlobalUse', False)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(times, balances)
    plt.ylabel('Ethereum')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%y'))

get_transactions(address)

#Streamlit app continued
if address:
    st.pyplot(get_transactions(address))
    st.text('Chart for: ')
    st.text(address)