#Import library and API key
from etherscan import Etherscan
from requests import get
from datetime import datetime
from matplotlib import pyplot as plt

BASE_URL = 'https://api.etherscan.io/api'
API_KEY = 'ENTER API KEY HERE'
ETH_VALUE = 10 ** 18

#Function to call the api endpoint
def make_api_url(module, action, address, **kwargs):
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
    transactions_url = make_api_url('account', 'txlist', address, startblock=0, endblock=99999999, page=1, offset=10000, sort='asc', apikey=API_KEY)
    response = get(transactions_url)
    data = response.json()['result']

    internal_tx_url = make_api_url('account', 'txlistinternal', address, startblock=0, endblock=99999999, page=1, offset=10000, sort='asc', apikey=API_KEY)
    response2 = get(internal_tx_url)
    data2 = response2.json()['result']

    data.extend(data2)
    data.sort(key=lambda x: int(x['timeStamp']))

    current_balance = 0
    balances = []
    times = []

    #Calculate value of ETH transferred to and from address
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

    #Create chart
    plt.plot(times, balances)
    plt.show()

get_transactions(address)


#TO DO later

#Get a list of 'ERC721 - Token Transfer Events' by Address
'''https://api.etherscan.io/api
   ?module=account
   &action=tokennfttx
   &contractaddress=0x06012c8cf97bead5deae237070f9587f8e7a266d
   &address=0x6975be450864c02b4613023c2152ee0743572325
   &page=1
   &offset=100
   &startblock=0
   &endblock=27025780
   &sort=asc
   &apikey=YourApiKeyToken'''

'''def nft_transfers(module, action, address, **kwargs):
    get_nft_transfers = '''


#Seperate tests below here------------------------
eth = Etherscan('ENTER API KEY HERE')
address ='Enter wallet address here'

#Set multiple wallet addresses
Wallet_Addresses = ["",
                    "",
                    ""]


#Get single wallet balance
eth_balance = eth.get_eth_balance(address)
#print('Eth Balance: ', float(eth_balance)/ETH_VALUE)

#Get multiple wallet balances
eth_balances = eth.get_eth_balance_multiple(Wallet_Addresses)
#print('Eth Balances: ', eth_balances)

#Get latest price of ETH
eth_price = eth.get_eth_last_price()
#print('Eth Price: ', eth_price)

#Get acc blanace by erc-20 token in USD value
Wallet_Address = ''
Contract_Address = '0xdAC17F958D2ee523a2206206994597C13D831ec7' #USDT contract address
acc_token_balance = eth.get_acc_balance_by_token_and_contract_address(address = Wallet_Address, contract_address = Contract_Address)
#print('USDT Balance: ', float(acc_token_balance)/100000)
