"""
Property of Maple Coin, Open source. 
To use any snippets of code or the entire script, you must mention appropriate credits for said script.
Developed by: Rudra Rupani, rudrarupani@maple-coin.com

///////////////////////////

Maple Coin

//////////////////////////

"""



from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(CryptoNode)
admin.site.register(transaction)
admin.site.register(block)
admin.site.register(sourceCode)
admin.site.register(miningSoftware)