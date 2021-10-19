from django.db import models
from django.utils import timezone
#from django.db.models.deletion import CASCADE
#from django.forms import ModelForm

class ShopAdmin(models.Model):
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

class Category(models.Model):
    def delete(self, *args, **kwargs):
        self.photo.delete()
        super(Category, self).delete(*args, **kwargs)
    name = models.CharField(max_length=255) #varchar = CharField
    detail = models.TextField() # text = TextField
    islive = models.BooleanField(default=1)
    # photo = models.ImageFiield (uplaod to ="pics") add to pic folder
    photo = models.ImageField() 
    
    def __str__(self):
        return self.name

class Slider(models.Model):
    def delete(self, *args, **kwargs):
        self.photo.delete()
        super(Slider, self).delete(*args, **kwargs)
    caption = models.CharField(max_length=128)
    photo = models.ImageField()
    islive = models.IntegerField()
       
class Product(models.Model):
    name = models.CharField(max_length=255) 
    categoryid = models.ForeignKey(Category,on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField()
    weight = models.IntegerField() 
    size = models.CharField(max_length=128)
    detail = models.TextField() 
    photo = models.ImageField()
    islive = models.IntegerField(default=1)
    
    def __str__(self):
        return self.name
    
class Gallary(models.Model):
    productid = models.IntegerField()
    photo = models.CharField(max_length=255)

class User(models.Model):
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    mobile = models.CharField(max_length=32)

class Bill(models.Model):
    userid = models.IntegerField()
    billdate  = models.DateField()
    amount = models.IntegerField()
    status = models.IntegerField() #order status 
    paymentmode = models.IntegerField() #payment mode 
    paymentstatus = models.IntegerField() #payment status 
    fullname = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    pincode = models.CharField(max_length=8)
    city = models.CharField(max_length=64)
    mobile = models.CharField(max_length=32)
    remarks = models.CharField(max_length=255)

class Cart(models.Model):
    productid = models.IntegerField()
    userid = models.IntegerField()
    quantity = models.IntegerField()
    price = models.IntegerField()
    billid = models.IntegerField(default=0)

class Pincodes(models.Model):
    city = models.CharField(max_length=255)
    code = models.IntegerField()

class Schools(models.Model):
    name= models.CharField(max_length=255)
    registerdate = models.DateField()
    islive = models.BooleanField(default=1)
    language = models.CharField(max_length=60)

class Testimonial(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField()
    detail = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    testimonial_date = models.DateField(null=True)

class Blog(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    heading = models.CharField(max_length=255)
    content = models.CharField(max_length=255)
    photo = models.ImageField()
    detail = models.CharField(max_length=255)
    blog_date = models.DateField(null=True)