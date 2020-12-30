from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from os import path
from json import dumps 
import datetime
from urllib.parse import urlparse, parse_qs
import requests
from django.http import HttpResponse,HttpResponseRedirect  

def index(request):
    return render(request,'index.html')

def contact(request):
    return render(request,'contact.html')

def about(request):
    return render(request,'about.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        password1 = request.POST['pass']
        password2 = request.POST['repass']
        email = request.POST['email']
        phone_no = request.POST['phone']
        cursor = connection.cursor()
        cursor.execute('''select USERNAME from customer where USERNAME = %s''',[username])
        row = cursor.fetchall()
        if (len(row) > 0 and row[0] == username):
                print("username already taken,please try with other username")
                messages.info(request,'username already taken..please try with other username')
                return redirect('register.html')
        print(row)
        if password1==password2:
            cursor = connection.cursor()
            cursor.execute("insert into customer(USERNAME,PASSWORD,NAME,PHONE_NUMBER,EMAIL_ID) values(%s,%s,%s,%s,%s)", [username,password1,first_name,phone_no,email])
            return redirect('/login')
        else:
             messages.info(request,'password not matching...')
             return redirect('register.html')
        return redirect("/")
    else:
        return render(request,'register.html')

def loginFlow(request):
     print("this is for login")
     if request.method == 'POST':
         username = request.POST['username']
         password = request.POST['password']
         cursor = connection.cursor()
         cursor.execute('''select USERNAME from customer where USERNAME = %s''',[username])
         userNameRow = cursor.fetchone()
         cursor.execute('''select PASSWORD from customer where PASSWORD = %s''',[password])
         passwordRow = cursor.fetchone()
         #print("password is " + passwordRow[0])
         if (userNameRow[0] == username ):
             if (passwordRow[0] == password):
                 print('Logged in successfully')
                 messages.info(request,'Logged in successfully')
                 response = HttpResponseRedirect("/")
                 response.set_cookie("royalusername",username)
                 return response
                 request.COOKIES['username']
         print("redirecting to home")        
         return redirect("/")
         print(row)
     else:
         return render(request,'login.html')
        
def carmodel(request):
    print("user is "+ request.COOKIES.get('royalusername'))
    return render(request,'carmodel.html')

def carmodel_details(request):
    path = request.get_full_path()
    id = path.split("=")
    print(id[1])
    cursor = connection.cursor()
    cursor.execute('''select * from car where MODEL_ID = %s''',[id[1]])
    row = cursor.fetchone()
    print("############")
    carDetails = {       
        'CAR_TYPE': row[1], 
        'MODEL_NAME': row[2], 
        'PRICE': row[3], 
        'FUEL_TYPE': row[4], 
        'TANSMISSION_TYPE': row[5],
        'SEATING': row [6],
        'CAR_COLOUR': row [7],
      }
    cursor.execute('''select * from car_detail where MODEL_ID = %s''',[id[1]])
    carInfo = cursor.fetchone()
    print(carInfo) 
    carDetails['ENGINE_CAPACITY'] = carInfo[1]
    carDetails['SEAT_COLOUR'] = carInfo[2]
    carDetails['WHEEL'] = carInfo[3]
    carDetails['SUNROOF'] = carInfo[4]
    carDetails['SMART_PARKING'] = carInfo[5]
    carDetails['AIRBAGS'] = carInfo[6]
    carDetails['MILEAGE'] = carInfo[7]
    carDetails['SPECIAL_FEATURE'] = carInfo[8]

    dataJson = dumps(carDetails)
    print(dataJson)
    return render(request,'carmodel-details.html',{'data':dataJson})

def testdrive(request):
    return render(request,'testdrive.html')

def testdrivesuccess(request):
    postData = request.POST.dict()
    MODEL_NAME = postData.get("browser")
    TEST_DRIVE_ADDRESS = postData.get("testdriveaddress")
    TEST_DRIVE_DATE = postData.get("testdrivedate")
    print(MODEL_NAME)
    cursor = connection.cursor()
    cursor.execute('''select * from car where MODEL_NAME=%s''',[MODEL_NAME])
    row = cursor.fetchone()
    MODEL_ID = row[0]
    cursor.execute('''insert into testdrive(MODEL_ID, TESTDRIVE_DATE,CUSTOMER_ADDRESS) values(%s,%s,%s)''', [ MODEL_ID, TEST_DRIVE_DATE,TEST_DRIVE_ADDRESS])
    return render(request, 'testdrivesuccess.html')

def customization(request):
    return render(request,'customization.html')

def purchase(request):
    pur = request.POST.dict()
    USERNAME = request.COOKIES.get('royalusername')
    MODEL_NAME = pur.get("browser")
    CAR_COLOUR = pur.get("CAR COLOUR")
    SEAT_COLOUR = pur.get("SEAT COLOUR")
    paymentMode =  pur.get("payment_mode")
    PACKAGE = pur.get("PACKAGE")
    PURCHASE_DATE =  pur.get("purchase_date")
    cursor = connection.cursor()
    cursor.execute('''select price from car where MODEL_NAME = %s''', [MODEL_NAME])
    price = cursor.fetchone()
    totalPrice = price[0]
    if(CAR_COLOUR == "MOUNTAIN GREY" or CAR_COLOUR == "DENIM BLUE" or CAR_COLOUR == "EMERALD GREEN"):
        totalPrice = totalPrice + 10000
    if(SEAT_COLOUR == "CARAMEL BROWN" or SEAT_COLOUR == "EXPRESSO BROWN" or SEAT_COLOUR == "RUBY RED"  ):
        totalPrice = totalPrice + 15000
    if(PACKAGE == "DRIVING ASSITANCE PACKAGE" or PACKAGE == "SMARTPHONE INTEGRATION PACKAGE" or PACKAGE == "DRIVING ASSITANCE PACKAGE" or PACKAGE == "LED INTELLIGENT LIGHT SYSTEM PACKAGE" or PACKAGE == "INDIVISUAL ENTERTAINMENT SYSTEM PACKAGE"  ):
        totalPrice = totalPrice + 20000
    cursor.execute('''insert into purchase(USERNAME, MODEL_NAME, FINAL_PRICE, PAYMENT_MODE, PURCHASE_DATE) values(%s,%s,%s,%s,%s)''', [USERNAME, MODEL_NAME, totalPrice, paymentMode, PURCHASE_DATE])
    cursor.execute('''SELECT LAST_INSERT_ID()''')
    lastInsertedId = cursor.fetchone()
    cursor.execute('''select * from purchase where PURCHASE_ID = %s''',[lastInsertedId[0]])
    row = cursor.fetchone()
    purchase_summary = {       
        'USERNAME': row[1], 
        'MODEL_NAME': row[2], 
        'FINAL_PRICE': row[3], 
      }
    dataJson = dumps(purchase_summary)
    print(dataJson)
    return render(request,'purchase.html',{'data':dataJson})
    return render(request,'purchase.html')
