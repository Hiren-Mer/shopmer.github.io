from django.contrib import admin
# from .models import Pincodes
from .models import Product
from .models import Category


# @admin.register(Pincodes)
# class PincodesAdmin(admin.ModelAdmin):
#     list_display = ['city','code']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','categoryid','price','quantity','weight','size','detail','photo','islive']   
    

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']