"""
Property of Maple Coin, Open source. 
To use any snippets of code or the entire script, you must mention appropriate credits for said script.
Developed by: Rudra Rupani, rudrarupani@maple-coin.com

///////////////////////////

Maple Coin

//////////////////////////

"""



from django.db import models

# Create your models here.

class CryptoNode(models.Model):
    username = models.CharField(max_length=64)
    address = models.CharField(max_length=512)

    publicKey = models.CharField(max_length=2048)
    exponent = models.CharField(max_length=2048)

    d = models.CharField(max_length=2048)
    p = models.CharField(max_length=2048)
    q = models.CharField(max_length=2048)

    currentBalance = models.FloatField()

class transaction(models.Model):
    sender = models.CharField(max_length=512, unique=False)
    reciever = models.CharField(max_length=512, unique= False)

    amount = models.FloatField(unique= False)

    timeOfTransaction = models.DateTimeField(unique_for_date= False)

    signature = models.BinaryField()

    block = models.IntegerField(unique=False, null=True)

class block(models.Model):
    previousBlockHash = models.CharField(max_length=512, null=True)

    merkelRoot = models.CharField(max_length=512)

    nonce = models.CharField(max_length=1024, unique=False)
    blockHash = models.CharField(max_length=512)

    blockTime = models.DateTimeField(unique_for_date=False)
    miner = models.CharField(max_length=512, unique=False)

class sourceCode(models.Model):
    name = models.CharField(max_length=512, null=False)
    version = models.CharField(max_length=512, null=False)
    sourceFile = models.FileField(upload_to='media')

class miningSoftware(models.Model):
    name = models.CharField(max_length=512, null=False)
    version = models.CharField(max_length=512, null=False)
    sourceFile = models.FileField(upload_to='media')