address_nft = address


#Using the INFURA API to find the most expensive NFT purchase

# Get the transaction count for the given Ethereum address
tx_count = web3.eth.getTransactionCount(address)

# Initialize an empty list to store the transactions
transactions = []

# Get the transactions for the given Ethereum address
for i in range(tx_count):
    # Get the transaction hash
    tx_hash = web3.eth.getTransaction(i)['hash']

    # Get the transaction data
    tx_data = web3.eth.getTransaction(tx_hash)

    # Add the transaction data to the list
    transactions.append(tx_data)


# Initialize variables to keep track of the most expensive NFT purchase
most_expensive_nft_value = 0
most_expensive_nft_to = None
most_expensive_nft_input = None

# Iterate over the transactions
for tx in transactions:
    # Check if the transaction has a value
    if 'value' in tx:
        # Check if the transaction value is higher than the current most expensive NFT value
        if tx['value'] > most_expensive_nft_value:
            # Update the most expensive NFT value, recipient address, and input data
            most_expensive_nft_value = tx['value']
            most_expensive_nft_to = tx['to']
            most_expensive_nft_input = tx['input']

# Set input_data to the transaction input data with the highest value
input_data = most_expensive_nft_input


def parse_nft_input_data(input_data):
    # Check if the input data is None
    if input_data is None:
        # If the input data is None, return an empty dictionary
        return {}

    # The input data is a hexadecimal string, so we need to decode it
    input_data_decoded = bytes.fromhex(input_data[2:])

    # The first 4 bytes of the input data contain the method signature
    # The next 32 bytes contain the token ID
    # The next 20 bytes contain the recipient address
    # The rest of the input data is not used in this example
    method_signature = input_data_decoded[0:4]
    token_id = input_data_decoded[4:36]
    recipient_address = input_data_decoded[36:56]

    # Return the method signature, token ID, and recipient address as a dictionary
    return {
        'method_signature': method_signature,
        'token_id': token_id,
        'recipient_address': recipient_address,
    }




# Parse the input data to extract the details of the most expensive NFT purchase
nft_details = parse_nft_input_data(most_expensive_nft_input)

# Print the details of the most expensive NFT purchase
# print('Most expensive NFT purchase:')
# print('Value:', most_expensive_nft_value)
# print('Recipient address:', most_expensive_nft_to)
# print('NFT details:', nft_details)



#Most expensive NFT purchase
# Print the details of the most expensive NFT purchase
st.subheader('NFTs')
st.markdown('**Most expensive NFT purchase:**')
st.markdown('Value: %.3F' % (most_expensive_nft_value))
st.markdown('Recipient address: ', most_expensive_nft_to)
st.markdown('NFT details: ', nft_details)