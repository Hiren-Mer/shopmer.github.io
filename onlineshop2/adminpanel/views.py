from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.utils.html import escapejs
from django.contrib.auth.hashers import make_password
from .forms import PincodesForm,SchoolsForm,CategoriesForm,SliderForm
from .forms import ProductForm,UserForm,TestimonialForm,BlogForm
from .models import Category,User
from .models import Schools,Cart,Bill
from .models import Pincodes,Testimonial,Blog
from .models import Product,ShopAdmin,Slider
# from django.contrib.auth.hashers import make_password
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings
from django.db import connection
from datetime import datetime
# from django.core import serializer
from django.db.models import Count


import random
import string
import json 


#ajax code here

def loaddemo(request):
    return render(request,"loaddemo.html")

def ajaxloaddemo(request):
    CurrentDateTime = datetime.now()
    output = CurrentDateTime.strftime("%d-%m-%Y %H:%M:%S %p")
    return HttpResponse(output)

def getdemo(request):
    return render(request, "getdemo.html")

def getmethoddemo(request):
    #print(data)
    #print(request.GET['data'])
    data = request.GET; #create dictionary which has all input required
    products = Product.objects.filter(name=data['name'])
    output = f"<table border='1' align='center' cellpadding='2' width='80%'>";
    for product in products:
        output = output + f"<tr><td>{product.name}</td><td>{product.price}</td><td>{product.quantity}</td><tr>"
    output = output + "</table>"
    #print(output)
    return HttpResponse(output)

def postdemo(request):
    return render(request, "postdemo.html")

# def postmethoddemo(request):
#     product_name = request.POST["txtproduct"]
#     products = Product.objects.filter(name=product_name)
#     json = []
#     for product in products:
#         row = {"name":product.name,"price":product.price,"quantity":product.quantity,"id":product.id}
#         json.append(row)
#     return JsonResponse(json, safe=False)
def deletemethoddemo(request):
    data = request.GET
    temp = Product.objects.get(id=data['productid'])
    temp.delete()
    return HttpResponse("1")

def updateproductusingajax(request):
    data = request.GET
    product = Product.objects.get(id=data['productid'])
    product.name = data['name']
    product.price = data['price']
    product.quantity = data['quantity']
    product.save()
    return HttpResponse("1")
def insertusingajaxdemo(request):
    data = request.GET
    product = Product()
    product.categoryid = '1'
    product.weight = 0
    product.name = data['name']
    product.price = data['price']
    product.quantity = data['quantity']
    product.save()
    return HttpResponse("1")
def postmethoddemo(request):
    product_name = request.POST["txtproduct"]
    products = Product.objects.filter(name=product_name)
    json = []
    for product in products:
        row = {"name":product.name,"price":product.price,"quantity":product.quantity,"id":product.id}
        json.append(row)
    return JsonResponse(json, safe=False)

def addtocart(request):
    data = request.GET
    json = []
    if not 'userid' in request.session:
        row = {"success":'No',"message":'login required'}
        json.append(row)
    else:
        #user has logged in 
        productid = data["productid"]
        userid = request.session["userid"]
        quantity = 1
        count = Cart.objects.filter(productid=productid,userid=userid,billid=0).count()
        if count==0: #no product previously added into cart
            cart = Cart(productid=productid,userid=userid,quantity=quantity,price=0,billid=0)
            cart.save()
        else:   #user has already added this product into cart
            cart = Cart.objects.get(productid=productid,userid=userid,billid=0)
            cart.quantity = cart.quantity + 1
            cart.save()
        row = {"success":'Yes',"message":'Cart Updated'}
        json.append(row)
    return JsonResponse(json, safe=False)

def getcartdata():
    sql = "select p.id,p.name,p.price,p.photo,p.name,c.id 'cartid',c.quantity 'cart_quantity', p.price * c.quantity 'total' from adminpanel_product p, adminpanel_cart c where c.userid=userid and  productid=p.id and billid=0 order by c.id desc";
    table = Product.objects.raw(sql) 
    return table

def deletefromcart(request):
    data = request.GET
    temp = Cart.objects.get(id=data['cartid'])
    temp.delete()
    return HttpResponse('1')



########################################################################################
def frontend_test(request):
    return render(request,"frontend_template.html")

def product_detail(request,productid):
    product = Product.objects.get(id=productid)
    #select * from product where id=productid
    return render(request, "frontend_product_detail.html",{"product":product})

def cart(request):
    if not 'userid' in request.session:
        return redirect("login")
    else:
        userid = request.session["userid"]
        table = getcartdata()
        return render(request, "frontend_cart.html",{"table":table,"userid":userid})
def checkout(request):
    userid = request.session["userid"]
    if not 'userid' in request.session:
        return render(request, "frontend_login.html")
    else:
        if request.method != "POST":
            #step 1 fetch total of the product added into cart
            sql = f"select p.id 'productid',c.id,sum(p.price * c.quantity) 'grand_total' from adminpanel_product p, adminpanel_cart c where c.userid={userid} and  productid=p.id and billid=0";
            total = Product.objects.raw(sql) 
            return render(request, "frontend_checkout.html",{"total":total}) 
        else:
            #step1 fetch all product which user has added into cart
            sql = "select p.id 'productid',c.id,p.name,p.price 'product_price',c.quantity 'order_quantity',p.quantity 'stock'  from adminpanel_product p, adminpanel_cart c where c.userid=userid and productid=p.id and billid=0"
            cart = Product.objects.raw(sql) 
            
            #step2 findout if whether each item is in stock or not 
            out_of_stock = [] #empty list (used to hold out of stock product ids)
            for cart_row in cart:
                if cart_row.stock<cart_row.order_quantity:
                    tuple = (cart_row.productid,cart_row.name)
                    out_of_stock.append(tuple)
            if len(out_of_stock)>=1: #one more product is out of stock
                table = getcartdata()
                return render(request, "frontend_cart.html",{"table":table,"out_of_stock":out_of_stock})
            else: #all product are in stock 
                ##calculate grand total of order and reduce stock of that product which is add into cart as well as update cart price
                grand_total=0
                cursor = connection.cursor();
                for cart_row in cart:
                    sql = f"update adminpanel_product set quantity=quantity-{cart_row.order_quantity} where id={cart_row.productid}"
                    cursor.execute(sql);
                    
                    sql = f"update adminpanel_cart set price={cart_row.product_price} where id={cart_row.id}"
                    cursor.execute(sql);
                    
                    grand_total= grand_total + (cart_row.product_price * cart_row.order_quantity)    
                #insert row into order
                bill = Bill()
                bill.userid = userid
                CurrentDateTime = datetime.now()
                output = CurrentDateTime.strftime("%Y-%m-%d")
                bill.billdate = output
                bill.amount = grand_total
                bill.status = 1
                bill.paymentmode = 1
                bill.paymentstatus = 1
                bill.fullname = request.POST.get('firstname') + " " + request.POST.get('lastname')
                bill.address1 = request.POST.get('address1')
                bill.address2 = request.POST.get('address2')
                bill.pincode = request.POST.get('zipcode')
                bill.city = request.POST.get('city')
                bill.mobile = request.POST.get('phone')
                bill.remarks = request.POST.get('remarks')
                bill.save()
                billid = bill.id
                #update billid in cart table 
                sql = f"update adminpanel_cart set billid={billid} where billid=0 and userid={userid}"
                cursor.execute(sql)
            return render(request, "frontend_cart.html",{"message":"order placed successfully","orderid":billid})

def frontend_logout(request):
    if 'userid' in request.session:
        del request.session["userid"]
    return redirect("/home")
def user_login(request):
    if request.method == "POST":  # user has submitted input
        email = request.POST["txtemail"]
        user_given_password = request.POST["txtpassword"]
        count = User.objects.filter(email=email).count()
        if count == 1:  # login successfull
            hashed_password = User.objects.only("password").get(email=email).password
            # now compare user given password with hashed_password
            try:
                password_hasher = PasswordHasher()
                if password_hasher.verify(hashed_password, user_given_password) == True:
                    # successful login
                    id = User.objects.only("id").get(email=email).id
                    request.session["userid"] = id
                    blogs = Blog.objects.values_list('id','title','author','blog_date','detail','photo','content')
                    yes = 1
                        # all lives products show
                    products = Product.objects.values_list('id','name','photo','price').filter(islive=yes)
                    return render(request, 'frontend_home.html',{"blogs":blogs,"products":products})
            except VerifyMismatchError:
                return render(request, "frontend_login.html", {"message": "invalid login attempt"})
        else:
            return render(request,"frontend_login.html",{"message":"invalid login attempt"})
    else: 
        if not 'message' in request.session:
            return render(request,"frontend_login.html")
        else:
            message = request.session["message"]
            del request.session["message"]
            return render(request,"frontend_login.html",{"message":message})
    return render(request,"frontend_login.html")
def user_register(request):   
    if request.method=="POST":
        email = request.POST["txtemail"]
        mobile = request.POST["txtmobile"]
        password = request.POST["txtpassword"]
        confirm_password = request.POST["txtconfirmpassword"]
        if password!=confirm_password:
             return render(request,"frontend_register.html",{"message":" password and confirm password do not match"})
        else:
            # check email or mobile is already in use or not 
            email_count = User.objects.filter(email=email).count()
            mobile_count = User.objects.filter(mobile=mobile).count()
            if email_count>=1 or mobile_count>=1:
                 return render(request,"frontend_register.html",{"message":" email or mobile is already register with us"})
            else:
                password_hasher = PasswordHasher()
                hashed_password = password_hasher.hash(password)
                # run insert query 
                with connection.cursor() as cursor:
                    cursor.execute("insert into adminpanel_user (email,password,mobile) values (%s,%s,%s) ",[email,hashed_password,mobile])
                    cursor.close()
                    request.session["message"] = "register successfully" 
                return redirect("/login") 
    return render(request,"frontend_register.html")
def user_forgot_password(request):
    return render(request,"frontend_forgot_password.html")
def user_change_password(request):
    if not 'userid' in request.session:
       return redirect("/login")
    if request.method=="POST":
        id = request.session["userid"]
        old_password = request.POST["txtcurrentpassword"]
        new_password = request.POST["txtpassword"]
        confirm_password = request.POST["txtpassword2"]
        if new_password!=confirm_password:
             return render(request,"frontend_change_password.html",{"message":"new password and confirm password do not match"})
        else:
            hashed_password = User.objects.only("password").get(id=id).password
            try:
                password_hasher = PasswordHasher()
                if password_hasher.verify(hashed_password,old_password)==True:
                    user = User.objects.get(id=id)
                    # hash password 
                    hashed_password = password_hasher.hash(new_password)
                    user.password = hashed_password
                    user.save()
                    return redirect ("/login")
            except VerifyMismatchError:
                 return render(request,"frontend_change_password.html",{"message":"invalid password"})
    return render(request,"frontend_change_password.html")
def frontend_category(request):
    yes = 1
    categories = Category.objects.values_list('id','name','photo').filter(islive=yes)
    #select id,name,photo from category where islive=yes
    return render(request,"frontend_category.html",{"categories":categories})

def frontend_product(request,categoryid):
    yes = 1
    products = Product.objects.values_list('id','name','photo','price').filter(islive=yes,categoryid=categoryid)
    #select id,name,photo,price from product where islive=yes and categoryid=categoryid
    return render(request,"frontend_product.html",{"products":products})

# def frontend_allproducts(request,productid):
#     yes = 1
#     # all products islive
#     allproducts = Product.objects.values_list('id','name','photo','price').filter(islive=yes)
#     return render(request,"frontend_product.html",{"allproducts":allproducts})

def frontend_home(request):
    blogs = Blog.objects.values_list('id','title','author','blog_date','detail','photo','content')
    yes = 1
    # all lives products show
    products = Product.objects.values_list('id','name','photo','price').filter(islive=yes)
    testimonial = Testimonial.objects.values_list('id','name','photo','designation','testimonial_date')
    return render(request,"frontend_home.html",{"blogs":blogs,"products":products,"testimonial":testimonial})

def blog_detail(request,blogid):
    blog = Blog.objects.get(id=blogid)
    return render(request,"frontend_blog_detail.html",{"blog":blog})

def frontend_testimonial(request,testimonialid):
    testimonial = Testimonial.objects.get(id=testimonialid)
    return render(request,"frontend_testimonial.html",{"testimonial":testimonial})

def send_text_email(subject,message,receiver_email_list):
    sender_email = settings.EMAIL_HOST_USER
    send_mail( subject, message, sender_email, receiver_email_list )
def generate_random_password(length=16):
    letters = string.ascii_lowercase + string.digits + string.ascii_uppercase + string.punctuation
    random_password = ''
    for i in range(length):
        random_password= random_password +  random.choice(letters)
    return random_password
def email(request):
    subject = 'hi This is email subject'
    message = "This is test email"
    recipient_list = ['hiren161616@gmail.com'] 
    send_text_email(subject,message,recipient_list)
    return HttpResponse("Email Send...")

def productid(self,request):
    prod = Cart.objects.get("productid")
    print(prod)
    return redirect("/")

def index(request):
    if request.method=="POST":
        email = request.POST["email"]
        #select id from shopadmin where email=email and password=password 
        count = ShopAdmin.objects.filter(email=email).count()
        if count==1: #login successfull 
            hashed_password = ShopAdmin.objects.only("password").get(email=email).password
            #now compare user given password with hashed_password
            user_given_password = request.POST["password"] 
            try:
                password_hasher = PasswordHasher()
                if password_hasher.verify(hashed_password,user_given_password)==True:
                    #successful login 
                    id =  ShopAdmin.objects.only("id").get(email=email).id
                    request.session["id"] = id
                    category = Category.objects.count()
                    pincode = Pincodes.objects.count()
                    product = Product.objects.count()
                    slider = Slider.objects.count()
                    user = User.objects.count()
                    testimonial = Testimonial.objects.count()
                    blog = Blog.objects.count()
                    classname = request.COOKIES["classname"]
                    context = {"email":email,"category":category,"classname":classname,"pincode":pincode,"product":product,"slider":slider,"user":user,"testimonial":testimonial,"blog":blog}  
                    response = render(request, "admin-dashboard.html",context)
                    expiry_time = 60 * 60 *  24 #in seconds
                    response.set_cookie("email_cookie",email,expiry_time)
                    response.set_cookie("classname","MerSoftTech International Company",expiry_time)
                    return response             
            except VerifyMismatchError:
                return render(request,"admin_login.html",{"message":"invalid login attempt"})
        else:
            return render(request,"admin_login.html",{"message":"invalid login attempt"})
    return render(request,"admin_login.html")

def change_password(request):
    if not 'id' in request.session:
        return redirect("/")
    if request.method=="POST":
        id = request.session["id"]
        old_password = request.POST["txtoldpassword"]
        new_password = request.POST["txtnewpassword"]
        confirm_password = request.POST["txtconfirmpassword"]
        if new_password!=confirm_password:
             return render(request,"change_password.html",{"message":"new password and confirm password do not match"})
        else:
            hashed_password = ShopAdmin.objects.only("password").get(id=id).password
            try:
                password_hasher = PasswordHasher()
                if password_hasher.verify(hashed_password,old_password)==True:
                    shop_admin = ShopAdmin.objects.get(id=id)
                    # hash password 
                    hashed_password = password_hasher.hash(new_password)
                    shop_admin.password = hashed_password
                    shop_admin.save()
                    return redirect ("/logout")
            except VerifyMismatchError:
                 return render(request,"change_password.html",{"message":"invalid password"})
    return render(request,"change_password.html")

def forgot_password(request):
    if request.method=="POST":
        email = request.POST['email']
        count = ShopAdmin.objects.filter(email=email).count()
        #select count(*) from shopadmin where email=email
        if count==0:
             return render(request,"forgot_password.html",{"message":"email not registered with us"})
        else:
            #generate new random password
            new_password = generate_random_password(8)
            
            #hash password 
            password_hasher = PasswordHasher()
            hashed_password = password_hasher.hash(new_password)
            
            #update password into table 
            shop_admin =  ShopAdmin.objects.get(email=email)
            shop_admin.password = hashed_password
            shop_admin.save()
            
            #send newly generated plain password as email
            subject = "congratulation, we have recovered your account"
            message = f"your new password is {new_password}" 
            recipient_list = [email]
            send_text_email(subject,message,recipient_list)
            return redirect("/")
    return render(request,"forgot_password.html")

def logout(request):
    if not 'id' in request.session:
        return redirect("/")
    # delete session variable id 
    del request.session["id"]
    return redirect("/")

def signup(request):
    if request.method == "POST":
        user = ShopAdmin(email=request.POST['email'],password=request.POST['password'])
        user.save()
        return redirect("/")
    else:
        return render(request,"signup.html")
        
# def index(request):
#      if request.method=="POST":
#         email = request.POST["email"]
#         password = request.POST["password"]
#         #select id from shopadmin where email=email and password=password 
#         count = ShopAdmin.objects.filter(email=email,password=password).count()
#         if count==1: #login successfull 
#             id = ShopAdmin.objects.only("id").get(email=email,password=password).id 
#             request.session["id"] = id  
#             return render(request,"admin-dashboard.html")
#         else:
#             return render(request,"admin_login.html",{"message":"invalid login attempt"})
#      return render(request,"admin_login.html")


def admin_home(request):
    email = request.COOKIES["email_cookie"]
    classname = request.COOKIES["classname"]
    category = Category.objects.count()
    pincode = Pincodes.objects.count()
    product = Product.objects.count()
    slider = Slider.objects.count()
    user = User.objects.count()
    testimonial = Testimonial.objects.count()
    blog = Blog.objects.count()
    context = {"email":email,"classname":classname,"category":category,"pincode":pincode,"product":product,"slider":slider,"user":user,"testimonial":testimonial,"blog":blog}
    return render(request,"admin-dashboard.html",context)
     
def slider(request):
    if not 'id' in request.session:
        return redirect("/")
    table = Slider.objects.all()  
    return render(request,"slider.html",{"table":table})


def insert_slider(request):
    if not 'id' in request.session:
        return redirect("/")
    if request.method=="POST":
         form = SliderForm(request.POST,request.FILES)
         if form.is_valid():
             form.save() 
             table = Slider.objects.all() 
             return redirect("/slider")
    slider_form = SliderForm() 
    return render(request,"insert_slider.html",{"slider_form":slider_form})

def delete_slider(request,id):
    if not 'id' in request.session:
        return redirect("/")
    temp = Slider.objects.get(id=id)
    temp.delete()
    return redirect("/slider")

def edit_slider(request,id):
    if not 'id' in request.session:
        return redirect("/")
    table = Slider.objects.get(id=id)
    slider_form = SliderForm(instance=table)
    if request.method == "POST":
         form = SliderForm(data=request.POST, files=request.FILES, instance=table)
         if form.is_valid():
             form.save() 
             table = Slider.objects.all() 
             return render(request,"slider.html",{"table":table})
    context ={"slider_form":slider_form}
    return render(request,"edit_slider.html", context)


def user(request):
    if not 'id' in request.session:
        return redirect("/")
    table = User.objects.all()  
    return redirect("/user")

def insert_user(request):
    if not 'id' in request.session:
        return redirect("/")
    if request.method=="POST":
         form = UserForm(request.POST)
         if form.is_valid():
             form.save() 
             table = User.objects.all() 
             return render("/user")
    user_form = UserForm() 
    return render(request,"insert_user.html",{"user_form":user_form})

def edit_user(request,id):
    if not 'id' in request.session:
        return redirect("/")
    table = User.objects.get(id=id)
    user_form = UserForm(instance=table)
    if request.method=="POST":
         form = UserForm(request.POST, instance=table)
         if form.is_valid():
             form.save() 
             table = User.objects.all() 
             return render(request,"user.html",{"table":table})
    context = {'user_form':user_form}
    return render(request,'edit_user.html', context)

def delete_user(request,id):
    if not 'id' in request.session:
        return redirect("/")
    temp = User.objects.get(id=id)
    temp.delete()
    return redirect("/user")


def base(request):
    return render(request,"blank.html")
def parent(request):
    return render(request,'parent.html')
def test(request):
    return render(request,'test.html')
def tri(request):
    return render(request,'tri.html')

def triget(request):
    num1 = int(request.POST['txtnum1'])
    num = int(request.POST['txtnum'])
    for num in range(num1,num):
        BODY = (" "*(num1-num)+"*"*num)
        BODY = (" "*(num1-num)+"*"*num)
        BODY = (" "*(num1-num)+"*"*num)
        BODY = (" "*(num1-num)+"*"*num)
    
    return render(request,'triget.html',{"num1":num1,"num":num,"BODY":BODY})
def blank(request):
    return render(request,'blank.html')
def ifdemo(request):
    return render(request,'ifdemo.html')
def ifdemo2(request,age):
    return render(request,'ifdemo2.html',{'age':age})
def input(request):
    return render(request,'input.html')

def simpleinterest_get(request):
    amount = float(request.GET['txtamount'])
    rate = float(request.GET['txtrate'])
    year = float(request.GET['txtyear'])
    interest = (amount * rate * year) / 100
    return render(request,'interest.html', {'interest':interest,"amount":amount,"rate":rate,"year":year})

def input2(request):
    return render(request,"input2.html")

def maths_post(request):
    first = float(request.POST['txtfirst'])
    second = float(request.POST['txtsecond'])
    choice = int(request.POST['rdochoice'])
    result = 0
    if choice==1:
        result = first + second 
        operation = "+"
    elif choice==2:
        result = first - second 
        operation = "-"
    elif choice==3:
        result = first * second 
        operation = "*"
    elif choice==4:
        result = first / second 
        operation = "/"
    return render(request,"maths.html",{"result":result,"first":first,"second":second,"operation":operation})      

def bmi(request):
    return render(request,"bmi.html")

def bmiinterest(request):
    weight = float(request.POST['weight'])
    height = float(request.POST['height'])
    bmi = weight/(height/100)**2
    if bmi <= 18.4:
        BODY ="Underweight"
    elif bmi <= 24.9:
        BODY = "Healthy"
    elif bmi <= 29.9:
        BODY = " Over Weight"
    elif bmi <= 34.9:
        BODY = "Severely Over Weight"
    elif bmi <= 39.9:
        BODY = "Obese"
    else:
        BODY = "Severely Obese"
    return render(request,'bmiinterest.html', {'weight':weight,"height":height,"bmi":bmi,"BODY":BODY})

def pincodes(request):
    if not 'id' in request.session:
        return redirect("/")
    table = Pincodes.objects.all() #select * from pincodes 
    return render(request,"pincode.html",{"table":table})

def insert_pincode(request):
    if not 'id' in request.session:
        return redirect("/")
    if request.method=="POST":
         form = PincodesForm(request.POST)
         if form.is_valid():
             form.save() #insert a new record into table pincode
             table = Pincodes.objects.all() #select * from pincodes 
             return render(request,"pincode.html",{"table":table})
    pincode_form = PincodesForm() #create object of PincodesForm class of forms.py
    return render(request,"insert_pincode.html",{"pincode_form":pincode_form})

def delete_pincode(request,pincodeid):
    if not 'id' in request.session:
        return redirect("/")
    temp = Pincodes.objects.get(id=pincodeid)
    temp.delete()
    return redirect("/pincodes")

def edit_pincode(request,id):
    if not 'id' in request.session:
        return redirect("/")
    table = Pincodes.objects.get(id=id)
    pincode_form = PincodesForm(instance=table)
    if request.method=="POST":
         form = PincodesForm(request.POST, instance=table)
         if form.is_valid():
             form.save() 
             table = Pincodes.objects.all() 
             return render(request,"pincode.html",{"table":table})
    context = {'pincode_form':pincode_form}
    return render(request,'edit_pincode.html', context)

def schools(request):
    if not 'id' in request.session:
        return redirect("/")
    table = Schools.objects.all()  
    return render(request,"school.html",{"table":table})

def insert_school(request):
    if not 'id' in request.session:
        return redirect("/")
    if request.method=="POST":
         form = SchoolsForm(request.POST)
         if form.is_valid():
             form.save() 
             table = Schools.objects.all() 
             return render(request,"school.html",{"table":table})
    school_form = SchoolsForm() 
    return render(request,"insert_school.html",{"school_form":school_form})

def edit_school(request,schoolid):
    if not 'id' in request.session:
        return redirect("/")
    table = Schools.objects.get(id=schoolid)
    school_form = SchoolsForm(instance=table)
    if request.method=="POST":
         form = SchoolsForm(request.POST, instance=table)
         if form.is_valid():
             form.save() 
             table = Schools.objects.all() 
             return render(request,"school.html",{"table":table})
    context = {"school_form":school_form}
    return render(request,"edit_school.html", context)

def delete_school(request,schoolid):
    if not 'id' in request.session:
        return redirect("/")
    temp = Schools.objects.get(id=schoolid)
    temp.delete()
    return redirect("/schools")

def categories(request):
    if not 'id' in request.session:
        return redirect("/")
    table = Category.objects.all() 
    return render(request,"category.html",{"table":table})

def insert_categories(request):
     if not 'id' in request.session:
        return redirect("/")
     if request.method=="POST":
         form = CategoriesForm(request.POST,request.FILES)
         if form.is_valid():
             form.save() 
             table = Category.objects.all()  
             return redirect("/categories")
     categories_form = CategoriesForm()
     return render(request,"insert_category.html",{"categories_form":categories_form})

def delete_categories(request,id):
    if not 'id' in request.session:
        return redirect("/")
    temp = Category.objects.get(id=id)
    temp.delete()
    return redirect("/categories")

def edit_categories(request,id):
    if not 'id' in request.session:
        return redirect("/")
    table = Category.objects.get(id=id)
    categories_form = CategoriesForm(instance=table)
    if request.method == "POST":
         form = CategoriesForm(data=request.POST, files=request.FILES, instance=table)
         if form.is_valid():
             form.save() 
             table = Category.objects.all() 
             return render(request,"category.html",{"table":table})
    context ={"categories_form":categories_form}
    return render(request,"edit_category.html", context)

def products(request):
    if not 'id' in request.session:
        return redirect("/")
    # sql = "select p.id,p.name,price,quantity,p.photo,c.name 'categoryname' from adminpanel_product p,adminpanel_category c where categoryid=p.id"
    table = Product.objects.all()
    return render(request,"products.html",{"table":table})

def insert_product(request):
     if not 'id' in request.session:
        return redirect("/")
     if request.method=="POST":
         form = ProductForm(request.POST,request.FILES)
         if form.is_valid(): 
            form.save()
            table = Product.objects.all()
             
            return render(request,"products.html")
     products_form = ProductForm()
     return render(request,"insert_products.html",{"products_form":products_form})

def delete_product(request,id):
    if not 'id' in request.session:
        return redirect("/")
    temp = Product.objects.get(id=id)
    temp.delete()
    return redirect("/products")

def edit_product(request,id):
    if not 'id' in request.session:
        return redirect("/")
    table = Product.objects.get(id=id)
    products_form = ProductForm(instance=table)
    if request.method == "POST":
         form = ProductForm(data=request.POST,files=request.FILES,instance=table)
         if form.is_valid():
             form.save() 
             table = Product.objects.all() 
             return render(request,"products.html",{"table":table})
    context ={"products_form":products_form}
    return render(request,"edit_products.html", context)

def blog(request):
    if not 'id' in request.session:
        return redirect("/")
    table = Blog.objects.all()
    return render(request,"blog.html",{"table":table})

def insert_blog(request):
    if not 'id' in request.session:
        return redirect("/")
    if request.method=="POST":
         form = BlogForm(request.POST,request.FILES)
         if form.is_valid():
             form.save() 
             table = Blog.objects.all() 
             return redirect("/blog")
    else:     
        blog_form = BlogForm() 
    return render(request,"insert_blog.html",{"blog_form":blog_form})

def edit_blog(request,id):
    if not 'id' in request.session:
        return redirect("/")
    table = Blog.objects.get(id=id)
    blog_form = BlogForm(instance=table)
    if request.method == "POST":
         form = BlogForm(data=request.POST, files=request.FILES, instance=table)
         if form.is_valid():
             form.save() 
             table = Blog.objects.all() 
             return render(request,"blog.html",{"table":table})
    context = {"blog_form":blog_form}
    return render(request,"edit_blog.html", context)

def delete_blog(request,id):
    if not 'id' in request.session:
        return redirect("/")
    temp = Blog.objects.get(id=id)
    temp.delete()
    return redirect("/blog") 


def testimonial(request):
    if not 'id' in request.session:
        return redirect("/")
    table = Testimonial.objects.all()
    return render(request,"testimonial.html",{"table":table})

def insert_testimonial(request):
    if not 'id' in request.session:
        return redirect("/")
    if request.method=="POST":
         form = TestimonialForm(request.POST,request.FILES)
         if form.is_valid():
             form.save() 
             table = Testimonial.objects.all() 
             return redirect("/testimonial")
    testimonial_form = TestimonialForm() 
    return render(request,"insert_testimonial.html",{"testimonial_form":testimonial_form})

def edit_testimonial(request,id):
    if not 'id' in request.session:
        return redirect("/")
    table = Testimonial.objects.get(id=id)
    testimonial_form = TestimonialForm(instance=table)
    if request.method == "POST":
         form = TestimonialForm(data=request.POST, files=request.FILES, instance=table)
         if form.is_valid():
             form.save() 
             table = Testimonial.objects.all() 
             return render(request,"testimonial.html",{"table":table})
    context = {"testimonial_form":testimonial_form}
    return render(request,"edit_testimonial.html", context)

def delete_testimonial(request,id):
    if not 'id' in request.session:
        return redirect("/")
    temp = Testimonial.objects.get(id=id)
    temp.delete()
    return redirect("/testimonial") 

    