"""
Property of Maple Coin, Open source. 
To use any snippets of code or the entire script, you must mention appropriate credits for said script.
Developed by: Rudra Rupani, rudrarupani@maple-coin.com

///////////////////////////

Maple Coin

//////////////////////////

"""



from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.conf import settings
from MapleCoin.requestsAPIviews import *
from MapleCoin.HelperFuncs import *

# Create your views here.



"""

Home 

"""

def index(request):
    """
    Return the index page
    """

    return render(request, "MapleCoin/index.html", {
        "user" : request.user
    })

"""

End Home

"""



""" 

Wallet

"""

def wallet(request, message):
    """
    Return the wallet display page, check for user authentication, 
    if user is not logged in, return login page
    """

    #Check for authentication otherwise ask to login
    if request.user.is_authenticated:

        #get node and update balance
        node = CryptoNodes.get(username= request.user.username)
        getCurrentBalance(node)

        #return wallet page
        return render(request, "MapleCoin/wallet.html", {
            "message" : message,
            "username" : node.username,
            "publicKey" : node.publicKey,
            "exponent" : node.exponent,
            "address": node.address,
            "currentBalance": node.currentBalance,
            "transactions": getAllTransactions(node)[::-1]
        })

    else:

        #Ask to login
        return redirect('MapleCoin:login')
    
def addTransaction(request):
    """
    Perform a transaction 
    Lookout for post method
    Get all the details, do error checking to check for overspending,
    Wrong addresses, wrong keys, etc.
    """

    #Checking reuqest method
    if request.method == "POST":

        #Do error checking and verify transaction
        error = verifyUnknownTransaction(request)
        if error:

            #Transaction rejected, show error
            return redirect('MapleCoin:wallet', message= error)
        
        #Transaction data valid, Perform Transaction!
        error = performTransaction(request)
        if error:
            
            #Transaction rejected, show error (Unknown error)
            return redirect('MapleCoin:wallet', message= error)

        #Display the wallet page again
        return redirect('MapleCoin:wallet', message= ' ')

    #Method is get so simply ignore
    return redirect('MapleCoin:index')

"""

End Wallet

"""



"""

Login, Logout, registration 

"""

def loginView(request):
    """
    Render login page
    If the method is POST then authenticate the user 
    If authenticated then login user
    """     
    
    #checking request method
    if request.method == "POST":
        
        #Authenticating the user
        user = authenticate(request, username= request.POST["username"], password= request.POST["password"])

        #If a user is returned, correct user
        if user is not None:

            #login the user and display his wallet
            login(request, user)
            return redirect('MapleCoin:wallet', message= ' ')

        #wrong details
        else:
            
            #render the login page with error message
            return render(request, "MapleCoin/login.html", {
                "message" : 'Invalid Credentials',
            })
    
    #request method is get, render the login page
    return render(request, "MapleCoin/login.html")

def logoutView(request):
    """
    logout user
    """

    #simply logout user and take back to index
    logout(request)
    return redirect('MapleCoin:index')

def register(request):
    """
    Render the registration page
    if the request is post, register the user and render the wallet page
    If error, show username taken or password weak
    """

    #Checking for request method
    if request.method == "POST":

        #register the user
        error = registerUser(request)
        if error:

            #if there's an error, show it
            return render(request, "MapleCoin/registrationPage.html", {
                "message" : error
            })

        #Authenticate the user
        user = authenticate(request, username= request.POST["username"], password= request.POST["password"])

        if user is not None:

            #login the user
            login(request, user)

            #redirect to the wallet page
            return redirect('MapleCoin:wallet', message= ' ')

        else:

            #Error
            return render(request, "MapleCoin/registrationPage.html", {
                "message" : 'Unknown Error, Please contact the admin.'
            })

    #Request method is get, so simply render the registration page
    return render(request, "MapleCoin/registrationPage.html")

"""

End Login, Logout, registration 

"""



"""

Block Chain

"""

def blockChain(request):
    """
    Return the blockchain display page 
    """

    return render(request, "MapleCoin/BlockChain.html", {
        "blocks" : blocks.allRecords().order_by("-id")
    })

#Can be called from the above page to view the block in more detail
def viewBlock(request, id):
    """
    View a single Block and all its details 
    Argument: Block ID which is to be viewed
    Returns a page that shows the said block of ID in detail
    """

    return render(request, "MapleCoin/viewBlock.html", {
        "test": blocks.get(id= id),
        "transactions": transactions.filter(block= id)
    })

"""

End Block Chain

"""



"""

Transactions

"""

def showTransactions(request):
    """
    Show all the transactions
    """
    
    return render(request, "MapleCoin/transactionDetails.html", {
        "transactions": transactions.allRecords().order_by("-id")
    })

#Can be called from the above page to view the transaction in more detail
def viewTransaction(request, id, backType):
    """
    View a single Transaction and all its details
    Arguments: Transaction ID which is to be viewed, where the page is being called from
    Returns a page that shows the said transaction of ID in detail
    """
    
    return render(request, "MapleCoin/viewTransaction.html", {
        "transaction": transactions.get(pk= id[:-4]),
        "publicKey": CryptoNodes.get(address= transactions.get(pk= id[:-4]).sender).publicKey,
        "backType": id[-4:]
    })

#Can be called from any adress button to view the cryptonode in more detail
def viewCryptoNode(request, address):
    """
    View a single Crypto node and all its details
    Argument: Addess of the cryptonode which is to be viewed
    Returns a page that shows the said Crypto Node in detail
    """

    #Node object and balance
    node = CryptoNodes.get(address= address)
    getCurrentBalance(node)

    #Show node
    return render(request, "MapleCoin/viewCryptoNode.html", {
        "node": node,
        "transactions": getAllTransactions(node)[::-1]
    })

"""

End Transactions

"""



"""

Mining 

"""

def mining(request):
    """
    Return the mining display page
    """
    try:
        return render(request, "MapleCoin/Mining.html", {
            "miningSoftwareFileWindows": miningSoftwareTable.get(name="LatestWindows"),
            "miningSoftwareFileMacOS": miningSoftwareTable.get(name="LatestMacOS"),
        })
    except:
        return render(request, "MapleCoin/Mining.html")

"""

End Mining

"""



"""

For Developers: Source Code

"""

def sourceCode(request):
    """
    For devs, to access a copy of the source code of the network
    Return and display the source code page
    """

    try:
        return render(request, "MapleCoin/sourceCode.html", {
            "sourceCodeFile": sourceCodeTable.get(name= "Latest")
        })
    except: 
        return render(request, "MapleCoin/sourceCode.html")

"""

End Source Code

"""