"""
Property of Maple Coin, Open source. 
To use any snippets of code or the entire script, you must mention appropriate credits for said script.
Developed by: Rudra Rupani, rudrarupani@maple-coin.com

///////////////////////////

Maple Coin

//////////////////////////

"""



from django.urls import path
from . import views

app_name = "MapleCoin"
urlpatterns = [
    path("", views.index, name="index"),
    # For API
    path("getPendingTransactions", views.getPendingTransactions, name="getPendingTransactions"),
    path("getInfoForNewBlock", views.getInfoForNewBlock, name="getInfoForNewBlock"),
    path("getSignature", views.getSignature, name="getSignature"),
    path("uploadBlock", views.uploadBlock, name= "uploadBlock"),
    path("currentBlockSearchIndex", views.currentBlockSearchIndex, name= "currentBlockSearchIndex"),
    path("minerLogin", views.minerLogin, name= "minerLogin"),
    path("getBlockChain", views.getBlockChain, name="getBlockChain"),
    path("getTransactions", views.getTransactions, name="getTransactions"),
    path('downloadBlockChain', views.getBlockChain, name="downloadBlockChain"),
    path('downloadTransactions', views.getTransactions, name="downloadTransactions"),
    path('downloadNodeTransactions/<str:address>', views.getNodeTransactions, name="downloadNodeTransactions"),
    path('downloadInfo/<str:address>', views.nodeInfo, name='nodeInfo'),
    path('downloadBlock/<str:id>', views.downloadBlock, name='downloadBlock'),
    path('downloadTransaction/<str:id>', views.downloadTransaction, name='downloadTransaction'),

    #For Web
    path("login", views.loginView, name="login"),
    path("logout", views.logoutView, name= "logout"),
    path('register', views.register, name="register"),
    path('addTransaction', views.addTransaction, name= "addTransaction"),
    path('wallet/<message>', views.wallet, name="wallet"),
    path('transactions', views.showTransactions, name= "transactions"),
    path('blockChain', views.blockChain, name= "BlockChain"),
    path('mining', views.mining, name= 'mining'),
    path('sourceCode', views.sourceCode, name='sourceCode'),
    path('viewTransaction/<str:id><str:backType>', views.viewTransaction, name="viewTransaction"),
    path('viewBlock/<str:id>', views.viewBlock, name="viewBlock"),
    path('viewCryptoNode/<str:address>', views.viewCryptoNode, name="viewCryptoNode")
]

