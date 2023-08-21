from xrpl.transaction import submit_and_wait
from xrpl.models.transactions.nftoken_mint import NFTokenMint, NFTokenMintFlag
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.requests import AccountNFTs
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
import base58
import ipfsApi

api = ipfsApi.Client('127.0.0.1', 5001)

meta_data = {
    "title": "NFT_image",
    "description": "we are trying to create a NFT",
    "author": "Aman Pandey",
    # 'file_path':'C:/Users/HP/Downloads/NFTimage.jpg',

    # Add other metadata fields as needed
}
print(meta_data)
res = api.add("C:/Users/balaj/Desktop/nft.jpg")   #add image path
image_dict=(res)[0]
ipfs_cid=(image_dict.get('Hash'))
print(ipfs_cid)

ipfs_bytes = base58.b58decode(ipfs_cid)
print(ipfs_bytes)

 
# Convert IPFS CID to bytes and then to hexadecimal

ipfs_hex = ipfs_bytes.hex()

print("###################################### IPFS IMAGE_URI  ##################")
print(ipfs_hex)

# Connect to a testnet node

print("Connecting to Testnet...")
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)

# Get issuer account credentials from the testnet faucet
seed = ""
if seed == "":
    print("Requesting address from the Testnet faucet...")
    issuer_wallet = generate_faucet_wallet(client=client)
    issuerAddr = issuer_wallet.address
else:
    issuer_wallet = Wallet.from_seed(seed=seed)
    issuerAddr = issuer_wallet.address
print(f"\nIssuer Account: {issuerAddr}")
print(f"          Seed: {issuer_wallet.seed}")

# Construct NFTokenMint transaction to mint 1 NFT with IPFS URI

print(f"Minting an NFT for the image from IPFS...")
mint_tx = NFTokenMint(
    account=issuerAddr,
    nftoken_taxon=1,
    flags=NFTokenMintFlag.TF_TRANSFERABLE,
    uri=ipfs_hex, # Include the IPFS URI in the NFT metadata
)

# Sign mint_tx using the issuer account

mint_tx_response = submit_and_wait(transaction=mint_tx, client=client, wallet=issuer_wallet)
mint_tx_result = mint_tx_response.result

print(f"\n  Mint tx result: {mint_tx_result['meta']['TransactionResult']}")
print(f"     Tx response: {mint_tx_result}")

for node in mint_tx_result['meta']['AffectedNodes']:
    if "CreatedNode" in list(node.keys())[0]:
        print(f"\n - NFT metadata:"
              f"\n        NFT ID: {node['CreatedNode']['NewFields']['NFTokens'][0]['NFToken']['NFTokenID']}"
              f"\n  Raw metadata: {node}")

# Query the minted account for its NFTs

 
get_account_nfts = client.request(
    AccountNFTs(account=issuerAddr)
)

nft_int = 1

print(f"\n - NFTs owned by {issuerAddr}:")
for nft in get_account_nfts.result['account_nfts']:
    print(f"\n{nft_int}. NFToken metadata:"
          f"\n    Issuer: {nft['Issuer']}"
          f"\n    NFT ID: {nft['NFTokenID']}"
          f"\n NFT Taxon: {nft['NFTokenTaxon']}")

    nft_int += 1


