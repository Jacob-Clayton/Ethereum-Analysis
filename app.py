#Import libraries and env for API key
from requests import get
import requests
from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import streamlit as st
from dotenv import load_dotenv
import os 
import json
from web3 import Web3
from web3.providers import HTTPProvider
from collections import Counter


#Etherscan API URL
BASE_URL = 'https://api.etherscan.io/api'
#Infura API URL
INFURA_URL = 'https://mainnet.infura.io/v3/'
load_dotenv()
infura_api_key = os.getenv('INFURA_API_KEY')

#Formula to convert eth value into recognisable eth value
ETH_VALUE = 10 ** 18

#Function to configure the .env with the api key
def configure():
    load_dotenv()

#Streamlit App setup
st.title('Ethereum Account Analysis')
st.markdown('###### App to analyse the balance and interactions of any Ethereum address')

# Streamlit text entry box for eth address
address = st.text_input("Enter Ethereum Address or ENS Name: ")

# Create an HTTP provider that connects to an Ethereum node at the given URL
http_provider = HTTPProvider(f'https://mainnet.infura.io/v3/{infura_api_key}')

# Create a Web3 instance
web3 = Web3(http_provider)

# Check if the input value is an ENS name or an Ethereum address
if web3.isAddress(address):
    #If the input value is an Ethereum address, do nothing
    pass
else:
    #If the input value is an ENS name, convert it to the corresponding Ethereum address
    address = web3.ens.address(address)

# Create oringinal address because address is changed later
original_address = address

#Function to call the Etherscan API
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

    # Calculate the total number of transactions
    total_transactions = len(data)

    #Sort transactions by date
    data.sort(key=lambda x: int(x['timeStamp']))
    current_balance = 0
    balances = []
    times = []

    # Initialize variables to keep track of the highest transfer in and out of Ethereum
    max_transfer_in = 0
    max_transfer_in_date = None
    max_transfer_out = 0
    max_transfer_out_date = None
    # Initialize a variable to keep track of the total amount of ether spent on gas
    total_gas_spent = 0

    #Calculate value of ETH transferred externally and internally
    for tx in data:
        to = tx['to']
        value = int(tx['value'])/ETH_VALUE

        #Calculate ETH spent on gas
        if 'gasPrice' in tx:
            gas = int(tx['gasUsed']) * int(tx['gasPrice']) / ETH_VALUE
            total_gas_spent += int(tx["gasUsed"]) * int(tx["gasPrice"]) / ETH_VALUE
        else:
            gas = int(tx['gasUsed']) / ETH_VALUE
            total_gas_spent += int(tx["gasUsed"]) / ETH_VALUE

        #Convert total_gas_spent to a float and round it to 3 decimal places
        total_gas_spent = float(total_gas_spent)

        time = datetime.fromtimestamp(int(tx['timeStamp']))
        money_in = to.lower() == address.lower()        

        # Get ETH balance over time of the address
        if tx['isError'] == '0':
            if money_in:
                current_balance += value

                # Check if the current transfer is the highest transfer in
                if value > max_transfer_in:
                    # Update the maximum transfer in and the date of the transaction
                    max_transfer_in = value
                    max_transfer_in_date = time.strftime("%d %B %Y")
            else:
                current_balance -= value + gas

                # Check if the current transfer is the highest transfer out
                if value > max_transfer_out:
                    # Update the maximum transfer out and the date of the transaction
                    max_transfer_out = value
                    max_transfer_out_date = time.strftime("%d %B %Y")

        balances.append(current_balance)
        times.append(time)

    #print(current_balance)   
    current_balance = get_account_balance(address)

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


    #Preparing the table for most interacted with addresses
    transactions = data

    # Create a Counter to count the number of times each address appears in the "to" and "from" fields
    counts = Counter()

    # Iterate over the transactions and add the "to" and "from" addresses to the Counter
    for tx in transactions:
        counts[tx["to"]] += 1
        counts[tx["from"]] += 1

    # Get the 10 most common addresses using the most_common method
    top_addresses = counts.most_common(10)

    # Create a DataFrame of the top addresses using Pandas
    df = pd.DataFrame(top_addresses, columns=["Ethereum Address", "Count"])
    # Filter out the rows containing the user entered address
    df = df[df["Ethereum Address"] != address]
    # Rearranging index
    df.index = np.arange(1, len(df) + 1)

    total_received = 0
    total_sent = 0
    for transaction in transactions:
        value = int(transaction['value'])
        if value > 0:
            total_received += value
        else:
            total_sent += abs(value)
    total_received = total_received / ETH_VALUE
    total_sent = total_sent / ETH_VALUE

    values = []
    for transaction in transactions:
        value = int(transaction['value']) / ETH_VALUE
        values.append(value)


    # Set the style of the chart using the custom style
    with plt.style.context({
        'figure.facecolor': '#0E1117',
        'axes.facecolor': '#0E1117',
        'axes.grid': True,
        'grid.color': '#444444',
        'grid.linewidth': 0.5,
        'grid.alpha': 0.3,
        'text.color': '#ffffff',
        'xtick.color': '#ffffff',
        'ytick.color': '#ffffff', 
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'axes.labelcolor': '#ffffff',
        'axes.labelsize': 10,
        'axes.titlesize': 12,
        'lines.linewidth': 1.5,
        'font.family': 'sans-serif',
    }):

        #Create matplotlib chart on streamlit
        st.set_option('deprecation.showPyplotGlobalUse', False)   
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.plot(times, balances)
        plt.ylabel('Ethereum')
        plt.xticks(rotation=45)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
        st.pyplot()
        

        #Show address analysed details
        st.write('Ethereum Address: ', original_address)
        st.markdown('##')

        # Display max, min, and average balance on the page
        st.subheader('Analysis')
        st.markdown("Current balance: %.3f ETH" % (current_balance))
        st.markdown("Max balance: %.2f ETH on %s" % (max_balance, max_date))
        st.markdown("Min balance: %.3f ETH on %s" % (min_balance, min_date))
        st.markdown("Average balance: %.2f ETH over %d days" % (avg_balance, num_days))
        st.markdown("Total sent and received: %.2f ETH" % (total_received))
        # Print the total amount of ether spent on gas
        st.markdown("Total gas spent: %.2f ETH" % (total_gas_spent))
        # Print the total number of transactions
        st.markdown(f"Total transactions: {total_transactions}")

        # Print the highest transfer in and out of Ethereum and their respective dates
        st.markdown('The largest transfer in was %.2f ETH on %s' % (max_transfer_in, max_transfer_in_date))
        st.markdown('The largest transfer out was %.2f ETH on %s' % (max_transfer_out, max_transfer_out_date))
        st.markdown('##')

        # Top external interactions
        st.subheader('Address interactions')
        st.write(df.style.set_properties(align="center"))
        st.markdown('##')

        # Transacton Bar Chart
        st.subheader('Transaction History')
        st.bar_chart(values)


#Call function, comment out for final version because it is called later
#get_transactions(address)

#Create matplotlib chart on streamlit when an address is entered
if address:
    get_transactions(address)