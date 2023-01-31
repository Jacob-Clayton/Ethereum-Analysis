# Ethereum Analytics Tool

### Live here: https://jacob-clayton-etherscan-api-app-sblsnb.streamlit.app/

#### Bugs:
Code does not account for bridged ETH which can result in a negative balance if ETH is bridged out. Or a substantially overestimated balance if ETH is bridged in to the account.

#### To summarise what gthe code does:
1. Get api keys from .env and enter wallet address you want to analyse
2. Call two api endpoints
3. Get account balance
4. Get a list of all transactions by address
5. Calculate value of ETH transferred to and from address
6. Calculate ETH spent on gas for each transaction
7. Take external, internal and gas expenditure into account to calculate balance over time
8. Calculate max, min and avg balance plus they days they occured on.
9. Allow ENS entry as well as 0x address entry using the INFURA api
10. Customise matplotlib chart
11. Create chart (Balance vs time) with matplotlib
12. Host it all on streamlit, allowing the end user to enter an ethereum address


# API Sources
- https://etherscan.io/apis
- https://www.infura.io/
