from django.shortcuts import render , redirect
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import logout as log_out
from urllib.parse import urlencode
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint

HASHKEY = b'pRmgMa8T0INjEAfksaq2aafzoZXEuwKI7wDe4c1F8AY='


def home(request):
    return render(request,"index1.html")

def about(request):
    return render(request,"about.html")

def contact(request):
    return render(request,"contact.html")

def saveContact(request):
    name = request.GET.get("cname")
    mail = request.GET.get("email")
    msg = request.GET.get("message")
    print(name,mail,msg)
    return HttpResponse("Yes !")

def login(request): # /college/login
    msg = ""
    from django.db import connection
    err = request.GET.get("error")
    if err is not None:
        msg = "Invalid User !"

    if request.user:
        user = request.user
        auth0user = user.social_auth.get(provider='auth0')
        userdata = {
            'user_id': auth0user.uid,
            'name': user.first_name,
            'pass':user.password,
            # 'picture': auth0user.extra_data['picture'],
            'email': auth0user.extra_data['email']
        }
        mail = userdata['email']
        records=[]
        with connection.cursor() as cr:
            cr.execute("select type,uid,name,mail,branch from user where mail='{}'".format(mail))
            records = cr.fetchall()
        if len(records) == 0:
            return render(request,"login.html",{'userdata1':"Sucessfully Logged In.. Please fill the form below, to move ahead","userdata":userdata})
        else:
            type = records[0][0]
            id = records[0][1]
            name = records[0][2]
            email = records[0][3]
            branch = records[0][4]
            user = {"id":id,"name":name,"email":email,"branch":branch,"type":type}
            request.session['userdata'] = user
            if type == 1:
                return redirect("/student/home")
            else:
                return redirect("/faculty/home")
    return render(request,"login.html",{"msg":msg})

def register(request):
    from django.db import connection
    name = request.POST.get('username')
    email = request.POST.get('email_data')
    pwd = request.POST.get('pwd')
    type = request.POST.get('type')
    branch = request.POST.get('branch')
    print(request.POST)
    with connection.cursor() as cr:
        # cr = cnn.cursor()
        cr.execute(
    "insert into user(name,mail,password,type,branch) values (%s,%s,%s,%s,%s)",[name,email,pwd,type,branch])
        # cnn.commit()
        # cnn.close()
    with connection.cursor() as cr:
        # cr = cnn.cursor()
        cr.execute("select uid from user where mail = '{}'".format(email))
        id = cr.fetchall()[0][0]

    user = {"id":id,"name":name,"email":email,"branch":branch,"type":type}
    request.session['userdata'] = user
    print("Type is ",type)
    if type=="1": # faculty
        return redirect('/faculty/home')
    else: # student
        return redirect('/student/home')
    
    return redirect("/login")

def loginuser(request):
    email = request.POST.get('email')
    pwd = request.POST.get('pwd')

    from cryptography.fernet import Fernet
    cipher_suite = Fernet(HASHKEY)


    # query = "select * from user where mail='{0}' and password='{1}'".format(email,pwd)

    query = "select * from user where mail='{0}'".format(email)
    cnn = settings.CONNECTION()

    cr = cnn.cursor()
    cr.execute(query)
    record = cr.fetchone()
    if record is None:
        msg = "Login Failed !"
        return redirect('/college/login?error=1')
    ciphered_text = record[4]
    print(">>>>>",ciphered_text)
    ciphered_text = bytes(ciphered_text,"utf-8")
    try:
        unciphered_text = (cipher_suite.decrypt(ciphered_text))
        print("this is uncipherd txt>>>>>>",unciphered_text)
    except Exception as e:
        print(":Exception")

        return redirect("/college/login?error=1")


    if pwd != unciphered_text.decode("utf-8"):
        print("pwd not matched")
        msg = "Login Failed !"
        return redirect('/college/login?error=1')
    else:



        print(">>>>>> ",record)


        id = record[0]
        name = record[1]
        email = record[2]
        phone = record[3]
        branch = record[6]
        type = record[5]  # type

        isVerify = record[8] # 0
        if isVerify==1:
            return redirect('/college/verify')
        else:
            user = {"id":id,"name":name,"email":email,"phone":phone,"branch":branch,"type":type}

            request.session['userdata'] = user

            if type==1: # faculty
                return redirect('/faculty/home')
            else: # student
                return redirect('/student/home')

def verify(request):
    if request.method=="GET":
        return render(request,'verify.html')
    else:
        otp = request.POST.get('otp')
        mail = request.POST.get('email')
        query = "update user set isVerify=1 where mail='{0}' and otp={1}".format(mail,otp)
        cnn = settings.CONNECTION()
        cr = cnn.cursor()
        cr.execute(query)
        cnn.commit()
        return redirect('/college/login')




def logout(request):
    del request.session['userdata']
    log_out(request)
    return_to = urlencode({'returnTo': request.build_absolute_uri('/college/home/')})
    logout_url = 'https://%s/v2/logout?client_id=%s&%s' % \
                 (settings.SOCIAL_AUTH_AUTH0_DOMAIN, settings.SOCIAL_AUTH_AUTH0_KEY, return_to)
    return HttpResponseRedirect(logout_url)
    # return redirect('/college/home')


def sendMail(name,mail):
    otp = randomdigit(6)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "OTP Verification "
    msg['From'] = 'justsample4mail@gmail.com'
    msg['To'] = mail

    html = """
		<html>
		  <body>
		    <h1 style='color:red'>Email Confirmation</h1>
		    <hr>
		    <b>Welcome {0} , </b>
		    <br>
		    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
		    Your Registeration is successfully done, please verify your email with this otp <b>{1}</b>.
		    <br><br>
		    Thanks
		  </body>
		</html>
		""".format(name,otp)
    part2 = MIMEText(html, 'html')
    msg.attach(part2)


    fromaddr = 'gauravmaism2017@gmail.com'
    toaddrs  = mail
    username = 'justsample4mail@gmail.com'
    password = 'asdfg123@'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.quit()
    return otp

def randomdigit(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)
