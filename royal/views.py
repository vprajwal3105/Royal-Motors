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
        name = request.POST['name']
        username = request.POST['username']
        password1 = request.POST['pass']
        password2 = request.POST['repass']
        email = request.POST['email']
        phone_no = request.POST['phone']
        cursor = connection.cursor()
        row_count=cursor.execute('''select USERNAME from customer where USERNAME = %s''',[username])
        row = cursor.fetchone()
        if (row_count > 0 and row[0] == username):
            messages.info(request,'Username already taken, Please try with an other Username')      
            return redirect('/register') 
        if password1==password2:
            cursor = connection.cursor()
            cursor.execute("insert into customer(USERNAME,CUSTOMER_PASSWORD,CUSTOMER_NAME,PHONE_NUMBER,EMAIL_ID) values(%s,%s,%s,%s,%s)", [username,password1,name,phone_no,email])
            return redirect('/login')
        else:
             messages.info(request,'Password not matching')
        return redirect('/register')
    else:
        return render(request,'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        cursor = connection.cursor()
        row_count=cursor.execute('''select USERNAME,CUSTOMER_PASSWORD from customer where USERNAME = %s''',[username])
        userNameRow = cursor.fetchone()
        if(row_count == 0):
            messages.info(request,'Invalid Username or Password')
            return redirect('/login')
        if (userNameRow[0] == username and userNameRow[1]==password):
            response = HttpResponseRedirect("/")
            response.set_cookie("royalusername",username)
            return response
            request.COOKIES['username']
        else:
            messages.info(request,'Password is not matching')
            return redirect('/login')
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
    carDetails = {      
        'MODEL_ID': row[0], 
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
    TEST_DRIVE_DATE = postData.get("testdrivedate")
    print(MODEL_NAME)
    cursor = connection.cursor()
    cursor.execute('''select * from car where MODEL_NAME=%s''',[MODEL_NAME])
    row = cursor.fetchone()
    MODEL_ID = row[0]
    cursor.execute('''insert into testdrive(MODEL_ID, TESTDRIVE_DATE) values(%s,%s)''', [ MODEL_ID, TEST_DRIVE_DATE])
    return render(request, 'testdrivesuccess.html')

def customization(request):
    return render(request,'customization.html')

def purchase(request):
    pur = request.POST.dict()
    USERNAME = request.COOKIES.get('royalusername')
    MODEL_NAME = pur.get("browser")
    CAR_COLOUR = pur.get("CAR COLOUR")
    SEAT_COLOUR = pur.get("SEAT_COLOUR")
    paymentMode =  pur.get("payment_mode")
    PACKAGE = pur.get("PACKAGE")
    PURCHASE_DATE =  pur.get("purchase_date")
    cursor = connection.cursor()
    cursor.execute('''select MODEL_ID from car where MODEL_NAME = %s''', [MODEL_NAME])
    ID = cursor.fetchone()
    MODEL_ID = ID[0]
    cursor.execute('''select PRICE from car where MODEL_NAME = %s''', [MODEL_NAME])
    price = cursor.fetchone()
    totalPrice = price[0]
    if(CAR_COLOUR == "MOUNTAIN GREY" or CAR_COLOUR == "DENIM BLUE" or CAR_COLOUR == "EMERALD GREEN"):
        totalPrice = totalPrice + 10000
    if(SEAT_COLOUR == "CARAMEL BROWN" or SEAT_COLOUR == "EXPRESSO BROWN" or SEAT_COLOUR == "RUBY RED"):
        totalPrice = totalPrice + 15000
    if(PACKAGE == "DRIVING ASSITANCE PACKAGE" or PACKAGE == "SMARTPHONE INTEGRATION PACKAGE" or PACKAGE == "DRIVING ASSITANCE PACKAGE" or PACKAGE == "LED INTELLIGENT LIGHT SYSTEM PACKAGE" or PACKAGE == "INDIVISUAL ENTERTAINMENT SYSTEM PACKAGE"  ):
        totalPrice = totalPrice + 20000
    cursor.execute('''select * from customer where USERNAME = %s''', [USERNAME])
    CUS_ID=cursor.fetchone()
    CUSTOMER_ID=CUS_ID[0]
    cursor.execute('''insert into purchase(CUSTOMER_ID, MODEL_ID, FINAL_PRICE, PAYMENT_MODE, PURCHASE_DATE) values(%s,%s,%s,%s,%s)''', [CUSTOMER_ID, MODEL_ID, totalPrice, paymentMode, PURCHASE_DATE])
    cursor.execute('''SELECT LAST_INSERT_ID()''')
    lastInsertedId = cursor.fetchone()
    cursor.execute('''select * from purchase where PURCHASE_ID = %s''',[lastInsertedId[0]])
    row = cursor.fetchone()
    purchase_summary = {       
        'CUSTOMER_ID': row[1], 
        'MODEL_ID': row[2], 
        'FINAL_PRICE': row[3], 
      }
    dataJson = dumps(purchase_summary)
    print(dataJson)
    return render(request,'purchase.html',{'data':dataJson})
    return render(request,'purchase.html')
