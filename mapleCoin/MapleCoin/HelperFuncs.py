"""
Property of Maple Coin, Open source. 
To use any snippets of code or the entire script, you must mention appropriate credits for said script.
Developed by: Rudra Rupani, rudrarupani@maple-coin.com

///////////////////////////

Maple Coin 

//////////////////////////

"""



from .models import *
from django.conf import settings
from django.contrib.auth.models import User
import rsa, hashlib, datetime
from django.http import HttpResponse
import os

"""

Boiler Plate stuff

"""

#Hash Puzzle and Max Transactions
hashPuzzle, maxTransactions = "0000000", 200

#Setting block constant
blockConstant = 210000

#Key size for the RSA Keys
keySize = 2048

"""

End Boiler Plate stuff

"""



"""

SQL Tables

"""

class Table():
    """
    This is the table class is to enable Easy querying
    """

    def __init__(self, table):
        """
        Initialize the table
        """

        self.table = table

    def create(self, **kargs):
        """
        Create object in the said table
        """

        return self.table.objects.create(**kargs)

    def get(self, **kargs):
        """
        Get Object
        """

        return self.table.objects.get(**kargs)

    def filter(self, **kargs):
        """
        Filter
        """

        return self.allRecords().filter(**kargs)
    
    def checkInValuesList(self, obj, value):
        """
        Check if its in field
        """

        return (obj,) in self.table.objects.values_list(value)

    def allRecords(self):
        """
        All Records
        """

        return self.table.objects.all()

#For easier querying of the tables
blocks, transactions, CryptoNodes, sourceCodeTable, miningSoftwareTable = Table(block), Table(transaction), Table(CryptoNode), Table(sourceCode), Table(miningSoftware)

"""

SQL TABLES

"""



"""

Node Methods

"""

def getAllTransactions(node):
    """
    Get all the transactions of a given node
    """

    #Transactions where the node is the sender
    listOftransactions = list(transactions.filter(sender=node.address))
    #Extend with transactions where node is the reciver
    listOftransactions.extend(list(transactions.filter(reciever=node.address)))
    #Return the combination of both
    return listOftransactions

def getCurrentBalance(node):
    """
    Get the current balance of the node
    """

    #Getting all the transactions to calculate the current balance
    transactions = getAllTransactions(node)

    #Calculate balance, add if node is reciever else subtract if node is sender
    balance = 0
    for transact in transactions:
        if (node.address == transact.sender or node.address == transact.reciever):
            balance += (1 if transact.sender != node.address else -1) * int(transact.amount)

    #Update the balance of said node
    node.currentBalance = balance
    node.save()

    #Return balance
    return balance

"""

End Node Methods

"""



"""

Cryptographic Methods

"""

def createNewRSAKeys():
    """
    Generate new RSA keys 
    """

    return rsa.newkeys(keySize)

def getPrivateKey(node):
    """
    Craft and return a private key object for the given node
    """

    return rsa.PrivateKey(
        int(node.publicKey), 
        int(node.exponent), 
        int(node.d), 
        int(node.p), 
        int(node.q)
    )

def signMessage(message, privateKey):
    """ 
    Sign the message and return signature
    """

    return rsa.sign(
        message.encode('utf8'), 
        privateKey, 
        'SHA-512'
    )

def SHA3hash(string):
    """
    Get the SHA3 512 bit hash of a given string
    """

    return hashlib.sha3_512(string.encode('utf8')).hexdigest() 

"""

End Cryptographic Methods

"""



"""

User Registration

"""

def registerUser(request):
    """
    Register a user and create their crypto node
    using the data derived from the given request
    Return erros, return none if successful
    """

    #getting the data from the request
    username, password, retypePass, email = request.POST["username"], request.POST["password"], request.POST["retypepass"], request.POST["email"]
    
    #Checking for password, if correct then create user otherwise throw error
    if password != retypePass or len(password) < 8:
        #Weak password
        return 'Weak Password(Should be atleast 8 characters) or Paswords not matching'

    #OK password
    else:
        #Try creating a user
        try:
            user = createUser(username= username, password= password, email= email)
        #User already exists, throw error
        except:
            return f'Please Choose a different username, "{username}" is already taken.'

        #Create the public and private key pair for the said user
        publicKey, privateKey = createNewRSAKeys()

        #Create the Adress of the user from the public key
        address = SHA3hash(str(publicKey.n))

        #Create the Crypto Node of the user
        node = CryptoNodes.create(
            username= username,
            address = address,
            publicKey = publicKey.n,
            exponent = publicKey.e,
            d = privateKey.d,
            p = privateKey.p,
            q = privateKey.q,
            currentBalance = 0
        )
        
        return
    
"""

End User Registration

"""



"""

Transaction

"""

def performTransaction(request):
    """
    Perform a transaction according to the data provided by the request
    Return unknown erorr, return none if successful
    """

    try:
        #Pull data from the request
        sender, reciever, amount = request.POST["sender"], request.POST["reciever"], abs(float(request.POST["amount"]))

        #Get the sender node
        node = CryptoNodes.get(username= request.user.username)

        #Get the node's private key
        privateKey = getPrivateKey(node)

        #Get transaction time
        time = getCurrentDateTime()

        #Form the message according to Maple Coin's standards
        message = str(sender) + str(reciever) + str(float(amount)) + str(time)

        #Create the transaction signature of the said message
        signature = signMessage(message, privateKey)
        
        #Create a transaction object
        transactions.create(
            sender= sender, 
            reciever= reciever, 
            amount= amount, 
            timeOfTransaction= time, 
            signature=signature
        )

        return 

    except:
        return "Error: Unknown Error"

def verifyUnknownTransaction(request):
    """
    Get the required transaction data from the request and then perform necessary checks to make sure its valid 
        1.Check for valid data
        2.Check for valid user and node
        3.Check for modified HTML (modified sender, public key or amount)
        4.Check if valid reciver
        5.Check for sender == reciver
        6.Check for Overspending
        7.Unknown Error
    """
    
    #try block cus why not
    try:

        #check request method
        if request.method == "POST":
            #Get the required data

            #username
            username= request.user.username
            
            #Check if reciever and amount are entered
            try:
                reciever, amount = request.POST["reciever"], abs(float(request.POST["amount"]))
            except:
                return "Error: Please enter a reciever and amount"

            #get the sender, public key and exponent for checking
            sender, publicKey, exponent= request.POST["sender"], request.POST["publicKey"], request.POST["exponent"]

            #Check first if the user exists
            if not CryptoNodes.checkInValuesList(username, "username"):
                return "Error: You have tried to change the HTMl of the page, this is illegal and you may be sued for it."
            
            #get the node
            node = CryptoNodes.get(username= username)
            node.currentBalance = getCurrentBalance(node)
            
            #check for other errors
            return (   
                #Modified HTML (address, public key or exponent modified)
                "Error: You have tried to change either of sender address, publicKey or exponent through HTML, this is illegal and you may be sued for it."
                    if (str(publicKey) != str(node.publicKey) or str(exponent) != str(node.exponent) 
                    or str(sender) != str(node.address)) else 

                #Invalid reciver address
                "Error: The address that you have entered for reciever is invalid. Please Enter a valid address" 
                    if not CryptoNodes.checkInValuesList(reciever, "address") else

                #Sender == reciever
                "Error: You cannot send Maple Coins to yourself."
                    if node.address == reciever else 

                #Trying to send more than what they own
                "Error: You are trying to send more Maple Coins than you own. To earn more Maple Coins, you can mine blocks or buy Maple Coins."
                    if getCurrentBalance(node) < amount and node.address != "Miner Reward" else

                #Transaction verified, valid.
                None
            )

        else:  
            #Unknown Error
            return "Error: Unknown Error, please contact the admin."
            
    except: 
        #Unknown Error
        return "Error: Unknown Error, please contact the admin."
        
"""

End Transaction

"""



"""

Block

"""

def addBlock(data):
    """
    Create a block object from the given data and add it to the block chain
    Assign the transactions in the data their respective block numbers 
    Give miner reward
    """ 

    #Create the block object and add it to the blockchain
    blocks.create(
        previousBlockHash= list(blocks.allRecords())[-1].blockHash if len(list(blocks.allRecords())) > 0 else None,
        nonce = data["nonce"],
        blockHash= data["hash"],
        merkelRoot= data["merkelRoot"],
        blockTime= data["time"],
        miner= data["miner"]
    )
    
    #Assign the transactions the said created block (Put the transactions in the block)
    for i in transactions.filter(pk__in= eval(data["transactions"])):
        i.block = data["index"]
        i.save()
    
    #Give the miner reward
    minerReward = ((1/(2**(int(int(data["index"])/blockConstant))))*50) #Maple Coins
    time = getCurrentDateTime()

    #Create the transaction
    transactions.create(
        sender= "Miner Reward", 
        reciever= data["miner"], 
        amount= minerReward, 
        timeOfTransaction= time, 

        #Signature
        signature= signMessage(
            ("Miner Reward" + str(data["miner"]) + str(float(minerReward)) + str(time)),
            getPrivateKey(CryptoNodes.get(username= "CoinBase"))
        ), 

        block= data["index"]
    )

def parseBlockDataFromRequest(request):
    """
    Parse the data from the given request and return the testblock and data
    """

    #Parse data from request and return post and the said data in form of a block dict
    data = request.POST
    testBlock = {
        "index": data["index"],
        "previousBlockHash": data["previousBlockHash"],
        "nonce": data["nonce"],
        "blockHash": data["hash"],
        "merkelRoot": data["merkelRoot"],
        "blockTime": data["time"],
        "miner": data["miner"],
        "transactions": eval(data["transactions"])
    }

    return data, testBlock

"""

End Block

"""



"""

Block Verification

"""

def verifyBlock(testBlock):
    """
    Verify the given block
    """

    #verify the block index and check that its not an old block
    check0 = verifyBlockIndex(testBlock["index"])
    if not check0:
        return False

    #Verify the current block hash
    check1 = verifyBlockHash(testBlock)

    #verify the miner of the block
    check2 = verifyMiner(testBlock["miner"])

    #Verify the previous block hash
    check3 = verifyBlockPreviousHash(testBlock["previousBlockHash"])

    #Get the transaction objects of the transaction IDs mentioned in the block
    filteredTransactions = transactions.filter(pk__in= testBlock["transactions"])
    
    #Verify the Merkel Root of the given block
    check4 = verifyBlockMerkelRoot(filteredTransactions, testBlock["merkelRoot"])

    #Verify all the transactions
    check5 = verifyAllTransactions(filteredTransactions)

    #Make sure that every check is perfect
    return check0 == check1 == check2 == check3 == check4 == check5 == True

def verifyBlockIndex(index):
    """
    Verify if this is the new block everyone is looking for or an old that is already submitted
    """

    return (index == str(len(blocks.allRecords()) + 1))

def verifyMiner(minerAddress):
    """
    Check if the miner exists in the network
    """ 
    
    return CryptoNodes.checkInValuesList(minerAddress, "address")

def verifyBlockPreviousHash(givenPreviousBlockHash):
    """
    Veirfy the Block's previous hash by comparing it to current latest block hash
    """

    return givenPreviousBlockHash == (
        
        #Any other block
        list(blocks.allRecords())[-1].blockHash 
        if len(list(blocks.allRecords())) > 0 else 

        #Genesis block
        "None"
    )

#Block Hash verification
def verifyBlockHash(testBlock):
    """
    Verify the block hash
    """

    #Construct block hash from scratch and then compare it to the one that is recieved
    return SHA3hash(blockToString(testBlock)) == testBlock["blockHash"]

def blockToString(testBlock):
    """
    Convert the block object to a string representation that is
    upto the standards specified by Maple Coin Block Chain network
    Return the said string representation
    """

    return (
        str(testBlock["blockTime"]) + 
        testBlock["merkelRoot"] + 
        (testBlock["previousBlockHash"] if testBlock["previousBlockHash"] != "None" else "") + 
        str(testBlock["index"]) + 
        str(testBlock["nonce"])
    )
#Block Hash verification end

#Block Merkel Root verification
def verifyBlockMerkelRoot(filteredTransactions, merkelRoot):
    """
    Verify a block's Merkel Root
    If more than one transaction then calculate merkel root
    If one item then just the hash of the single item
    If no items then no Merkel root
    """
    #Merkel Root recursive calculation
    return getMerkelRoot([transactionToString(transact) for transact in filteredTransactions]) == merkelRoot

def getMerkelRoot(items):
    """
    Get the merkel root of a list of items
    """

    #Hash all the items in the given item list
    items = [SHA3hash(str(item)) for item in items]

    #Base condition, return the final merkel root
    if len(items) == 1:
        return items[0]
    elif len(items) == 0:
        return ""

    #add two hashes together and add the combined to the new items list
    newItems, temp = [], ""
    for index in range(len(items)):

        #If divisible by 2, save it for next iteration
        if index % 2 == 0:
            temp = items[index]
            if index == len(items) - 1:
                newItems.append(temp)
        else:
        #Otherwise add it to the saved item from previous iteration
            newItems.append(temp + items[index])
            temp = ""

    #repeat the process
    return getMerkelRoot(newItems)
#Block Merkel Root verification end

#All transactions verification
def verifyAllTransactions(filteredTransactions):
    """
    Verify each transaction in the list of transactions
    """

    return all([verifyTransaction(transact.id) for transact in filteredTransactions])

def verifyTransaction(pk):
    """
    Verify the given transaction object from the transaction id
    """

    #get the transaction object and its sender
    transact = transactions.get(pk= pk)

    #check that the sender and reciever are actual nodes
    check1 = (
        CryptoNodes.checkInValuesList(transact.sender, "address") and 
        CryptoNodes.checkInValuesList(transact.reciever, "address")
    )

    senderNode = CryptoNodes.get(address= transact.sender)

    #Check the signature of the transaction
    check2 = rsa.verify(
        transactionToString(transact).encode('utf8'), 
        transact.signature, 
        rsa.PublicKey(int(senderNode.publicKey), int(senderNode.exponent))
    )

    #Check that the transaction has not yet been assigned to a block
    check3 = transact.block is None

    #Make sure that every check it perfect
    return check1 == bool(check2) == check3 == True

def transactionToString(transact):
    """
    Convert the transaction object to a string representation that is
    upto the standards specified by Maple Coin Block Chain network
    Return the said string representation
    """

    return transact.sender + transact.reciever +  str(transact.amount) + str(transact.timeOfTransaction)[:-9]
#All transactions verification end

"""

End Block Verification

"""



"""

Miscellaneous Methods

"""

def getCurrentDateTime():
    """
    Current Date and time
    """

    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def createUser(**kargs):
    """
    Create User Object
    """

    return User.objects.create_user(**kargs)

def download(request, path):
    """
    Download Files
    """

    filePath = os.path.join(settings.MEDIA_ROOT)
    if os.path.exists(filePath):
        with open(filePath, 'rb') as givenFile:
            response = HttpResponse(
                givenFile.read(), 
                content_type= 'application/sourceFile'
            )
            response['Content-Disposition'] = 'inline;filename=' + os.path.basename(filePath)
        return response
    

"""

Miscellaneous Methods

"""
