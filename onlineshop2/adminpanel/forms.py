from django import forms
from datetime import datetime
from django.db.models import fields
from django.forms import widgets
from django.forms.fields import DateField
#from .forms import Pincodes,Schools,Category
from .models import Pincodes
from .models import Schools
from .models import Category
from .models import Product
from .models import User
from .models import Slider
from .models import Testimonial,Blog

class DateInput(forms.DateInput):
    input_type = 'date'

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name','photo','detail','designation','testimonial_date']
        widgets = {'mydate':DateInput()}
    
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Testimonial Name")
    photo = forms.FileField()
    detail = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Testimonial Detail")
    designation = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Testimonial Designation")
    testimonial_date = forms.DateField()

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title','author','heading','content','photo','detail','blog_date']
        widgets = {'mydate':DateInput()}
    
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Blog Name")
    author = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Author Name")
    heading = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Heading Name")
    content = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Content Blog")
    photo = forms.FileField()
    detail = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Blog Detail")
    blog_date = forms.DateField()


class SliderForm(forms.ModelForm):
    class Meta: 
        model = Slider
        fields = ['caption','photo','islive']
    caption = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Slider Caption")
    CHOICES = [('1','Yes'),('0','No')]
    islive = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES,label="is this Slider Live?")
    photo = forms.FileField()
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email','password','mobile'] 
    email = forms.CharField(label='Enter Email Id',max_length=128)
    password = forms.CharField(widget=forms.PasswordInput())
    mobile = forms.IntegerField()
        
class PincodesForm(forms.ModelForm):
    class Meta: 
        model = Pincodes
        fields = ['city','code']
    city = forms.CharField(label='Enter city',max_length=255)
    code = forms.IntegerField(label='Enter Pincode')

class SchoolsForm(forms.ModelForm):
    class Meta: 
        model = Schools
        fields = ['name','registerdate','islive','language']
    name = forms.CharField(label='Enter name',max_length=255)
    registerdate = forms.DateField(label='Enter Date')
    islive = forms.BooleanField(required=False )
    language = forms.CharField(label='Enter language')

class CategoriesForm(forms.ModelForm):
    class Meta: 
        model = Category
        fields = ['name','detail','islive','photo']
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Category Name")
    detail = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','rows':'5'}),label="Category Detail")
    CHOICES = [('1','Yes'),('0','No')]
    islive = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES,label="is this Category Live?")
    photo = forms.FileField()

class ProductForm(forms.ModelForm):
    class Meta:
         model = Product
         fields = ['name','categoryid','price','quantity','weight','size','detail','photo','islive']
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Product Name",required=True)
    categories = Category.objects.filter(islive=1).values('id','name')
    mycategories = []
    for category in categories:
        mycategories.append((category['id'],category['name']))
    categoryid = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}),choices=mycategories,label="Select Category",required=True)
    price = forms.CharField(widget=forms.NumberInput(attrs={'class':'form-control'}),label="Price",required=True)
    quantity = forms.CharField(widget=forms.NumberInput(attrs={'class':'form-control'}),label="Quantity",required=True)
    # weight = forms.CharField(widget=forms.NumberInput(attrs={'class':'form-control'}),label="Weight",required=True)
    size = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label="Size",required=True)
    detail = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','rows':'5'}),label="Product Detail")
    photo = forms.FileField()
    CHOICES = [('1','Yes'),('0','No')]
    islive = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES,label="is this Product Live?")

