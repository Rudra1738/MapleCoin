"""
Property of Maple Coin, Open source. 
To use any snippets of code or the entire script, you must mention appropriate credits for said script.
Developed by: Rudra Rupani, rudrarupani@maple-coin.com

///////////////////////////

Maple Coin

//////////////////////////

"""



from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import *
import json
from MapleCoin.HelperFuncs import *


"""

Transactions 

"""

#All transactions
def getTransactions(request):
    """
    Get all the transactions in JSON form
    """

    #Parse into JSON and return
    return HttpResponse(json.dumps({

        transact.id: {
            "sender" : transact.sender,
            "reciever": transact.reciever,
            "amount": transact.amount,
            "timeOfTransaction": str(transact.timeOfTransaction)[:-9],
            "publicKey": list(CryptoNodes.filter(address= transact.sender))[0].publicKey,
            "exponent": list(CryptoNodes.filter(address= transact.sender))[0].exponent
        }
        for transact in transactions.allRecords()

    }, indent= 4))

#Pending transactions
def getPendingTransactions(request):
    """
    Return the currently pending transactions that haven't been put into a block yet
    """

    #Parse all Transaction objects into JSON form
    return HttpResponse(json.dumps({

        transact.id: {
            "sender" : transact.sender,
            "reciever": transact.reciever,
            "amount": transact.amount,
            "timeOfTransaction": str(transact.timeOfTransaction)[:-9],
            "publicKey": list(CryptoNodes.filter(address= transact.sender))[0].publicKey,
            "exponent": list(CryptoNodes.filter(address= transact.sender))[0].exponent
        }

        for transact in transactions.allRecords() 
        if transact.block is None

    }, indent=4))

#Download transaction
def downloadTransaction(request, id):
    """
    Get all the avaiable info for the transaction requested
    """

    #Parse all data into json and return
    givenTransaction = transactions.get(id= id)
    return HttpResponse(json.dumps({

        "sender": givenTransaction.sender,
        "reciever": givenTransaction.reciever,
        "amount": givenTransaction.amount,
        "timeOfTransaction": str(givenTransaction.timeOfTransaction),
        "block":givenTransaction.block

    }, indent= 4))

#Signature of transaction
@csrf_exempt
def getSignature(request):
    """
    Return the signature of the transaction object of the given id
    """

    #Check request method and return signautre if exists else error
    if request.method == "POST":
        try:
            return HttpResponse(transactions.get(id= request.POST["id"]).signature)
        except:
            return HttpResponse("Transaction does not exist")

"""

End Transactions

"""



"""

Block Chain

"""

#Entire Block chain
def getBlockChain(request):
    """
    Return the Entire Block Chain in JSON
    """

    #Parse all the Block objects into JSON form
    return HttpResponse(json.dumps({

        givenBlock.id: {
            "previousBlockHash": givenBlock.previousBlockHash if givenBlock.previousBlockHash is not None else "",
            "merkelRoot": givenBlock.merkelRoot,
            "nonce": givenBlock.nonce,
            "blockHash": givenBlock.blockHash,
            "blockTime": str(givenBlock.blockTime)[:-9],
            "miner": givenBlock.miner
        }

        for givenBlock in blocks.allRecords()

    }, indent= 4))

#Download a block
def downloadBlock(request, id):
    """
    Get all the avaiable info for the block requested
    """

    #Parse all data into json and return
    givenBlock = blocks.get(id= id)
    return HttpResponse(json.dumps({

        "Block id": id,
        "Previous Block Hash": givenBlock.previousBlockHash,
        "merkelRoot": givenBlock.merkelRoot,
        "nonce": givenBlock.nonce,
        "hash": givenBlock.blockHash,
        "blockTime": str(givenBlock.blockTime),
        "miner": givenBlock.miner,

        #Including all the transactions in the block
        "transactions": {
            transact.id: {
                "sender" : transact.sender,
                "reciever": transact.reciever,
                "amount": transact.amount,
                "timeOfTransaction": str(transact.timeOfTransaction)[:-9],
                "publicKey": list(CryptoNodes.filter(address= transact.sender))[0].publicKey,
                "exponent": list(CryptoNodes.filter(address= transact.sender))[0].exponent
            }
            for transact in transactions.filter(block= id)
        }

    }, indent=4))

#New Block Info
def getInfoForNewBlock(request):
    """
    Return the info needed for the new block
    """
    
    #Return data in JSON form
    blockChain = list(blocks.allRecords())
    return HttpResponse(json.dumps({

        "id": str(blockChain[-1].id + 1) if len(blockChain) > 0 else str(1),
        "previousBlockHash": blockChain[-1].blockHash if blockChain != [] else "None",
        "hashPuzzle": hashPuzzle,
        "maxTransactions": maxTransactions

    }, indent= 4))

#Check which lock is currently being searched for
def currentBlockSearchIndex(request):
    """
    Return the current block index that is being searched
    """

    #index
    return HttpResponse(str(len(list(blocks.allRecords()))+1))

#Upload a block
@csrf_exempt
def uploadBlock(request):
    """
    Upload a block,
    Check for post method, get data, verify block, if valid, create block 
    Return Status "OK" = Block Accepted, "BAD" = Block rejected
    """ 

    #Checking request method
    if request.method == "POST":

        #Try the data, it may be faulty
        try:

            #Craft a block from the data
            data, testBlock = parseBlockDataFromRequest(request)

            #Verify said crafted block
            if verifyBlock(testBlock):

                #Create the block object and add it to the blockchain
                addBlock(data)
                return HttpResponse("OK")

            else: 
                #Block rejected cus verification failed
                return HttpResponse("BAD")
        
        #Faulty data
        except:

            #Block rejected due to improper data
            return HttpResponse("BAD")

    #Method is get so return bad
    else:
        return HttpResponse("BAD")

""" 

End Block Chain

"""



"""

Crypto Nodes

"""

def getNodeTransactions(request, address):
    """ 
    Get all the transactions of a node in JSON form and return it
    """

    #Parse into JSON and return
    return HttpResponse(json.dumps({

        transact.id: {
            "sender" : transact.sender,
            "reciever": transact.reciever,
            "amount": transact.amount,
            "timeOfTransaction": str(transact.timeOfTransaction)[:-9],
            "publicKey": list(CryptoNodes.filter(address= transact.sender))[0].publicKey,
            "exponent": list(CryptoNodes.filter(address= transact.sender))[0].exponent
        }

        for transact in getAllTransactions(CryptoNodes.get(address=address))

    }, indent= 4))


def nodeInfo(request, address):
    """
    Get all the avaiable info for the node requested and return it
    """
    
    #Parse all data into json and return
    node = CryptoNodes.get(address= address)
    return HttpResponse(json.dumps({

        "username": node.username,
        "address": node.address,
        "publicKey": node.publicKey,
        "exponent": node.exponent,
        "currentBalance": node.currentBalance,

        #Including all the transactions in the block
        "transactions": {
            transact.id: {
                "sender" : transact.sender,
                "reciever": transact.reciever,
                "amount": transact.amount,
                "timeOfTransaction": str(transact.timeOfTransaction)[:-9],
                "publicKey": list(CryptoNodes.filter(address= transact.sender))[0].publicKey,
                "exponent": list(CryptoNodes.filter(address= transact.sender))[0].exponent
            }
            for transact in getAllTransactions(node)
        }

    }, indent= 4))

"""

End Crypto Nodes

"""


"""

Miner

"""

@csrf_exempt
def minerLogin(request):
    """
    Login the miner and return the miner address
    """

    #checking for request method
    if request.method == "POST":
        username, password = request.POST["username"], request.POST["password"]
        try:
            #Login miner and return address
            login(request, authenticate(request, username= username, password= password))
            return HttpResponse(CryptoNodes.get(username= username).address)
        except:
            #Invalid credentials
            return HttpResponse("BAD")
    else:
        return HttpResponse("BAD")

"""

End Miner

"""