from flask import Flask, render_template, request, url_for, redirect, session,Response
import io
from sqlite3 import *
from flask_mail import Mail, Message
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('Agg')
from werkzeug.security import generate_password_hash, check_password_hash
a=[]
global var
def chart(n):
    print(n)
    print("h1")
    list_bmi = []
    list_weight = []
    con = None
    print("try!!!")
    # try:
    con = connect('BMI.db')
    cursor = con.cursor()
    sql1 = "select bmi from history where username='{}'".format(n)
    cursor.execute(sql1)
    data = cursor.fetchall()
    for d in data:
        print("hiiiii")
        list_bmi.append(float(str(d[0])))
        print(d[0])
    sql2 = "select weight from history where username='{}'".format(n)
    cursor.execute(sql2)
    data1 = cursor.fetchall()
    for f in data1:
        list_weight.append(float(str(f[0])))
        print(f[0])
    y=list_bmi[-5:]
    print("y=",y)
    x=list_weight[-5:]
    print("x=",x)
    plt.bar(x,y, width=0.6, color=['orange'])
    plt.title("Progress Chart ")
    plt.xlabel("BMI")
    plt.ylabel("Weight")
    plt.savefig('progresschart.png')
    sql = "select email from signup where username ='%s'"
    cursor.execute(sql % (username))
    data = cursor.fetchall()
    x=data[0][0]
    print(x)
    emsg = Message("Progress Report",sender="fitnessgig123@gmail.com", recipients=[x])
    emsg.body = "Your Current BMI is "+str(list_bmi[-1])+"\n"+"Attatched image is your Progress Report "+"\n" +"Hope You had a great time "+"\n"+"Thanks and Regards"+"\n"+"\n"+"FitnessGig Team"
    with app.open_resource("progresschart.png") as chart1:
        emsg.attach("progresschart.png", "image/png", chart1.read(),'inline')
    mail.send(emsg)
    # print(list_bmi)
    # print(list_weight)
    # print("hi")

app = Flask(__name__)
app.secret_key = "FitnessGig"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "fitnessgig123@gmail.com"
app.config["MAIL_PASSWORD"] = "fitnessgig@"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_ASCII_ATTACHMENTS"]=True
mail = Mail(app)

@app.route("/")
def index():
    if "username" in session:
        return render_template("index.html")
    else:
        return redirect(url_for('login'))


@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        global username
        username = request.form["username"]
        pword = request.form["pword"]
        # password1=generate_password_hash(pword, method='sha256')
        # print(password1)
        a.append(username)
        con = None
        try:
            con = connect("BMI.db")
            cursor = con.cursor()
            sql = "select * from signup where username ='%s'"
            cursor.execute(sql % (username))
            data = cursor.fetchall()
            sqlp="select password from signup where username='%s'"
            cursor.execute(sqlp % (username))
            data1=cursor.fetchall()
            pwd=data1[0][0]
            print(pwd)
            if check_password_hash(pwd,pword):
                if len(data) == 0:
                    return render_template("login.html", msg="invalid login")
                else:
                    session['username'] = username
                    # request.post(username) = username     
                    return redirect(url_for('index'))
            else:
                return render_template("login.html", msg="invalid login")
        except Exception:
            msg = "issue "
            return render_template("login.html", msg=msg)
    else:
        return render_template("login.html")


@app.route("/logout.html", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/signup.html", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        global username
        name = request.form["name"]
        contact = request.form["contact"]
        email = request.form['email']
        username = request.form["username"]
        pword1 = request.form["pword1"]
        pword2 = request.form["pword2"]
        if len(name)<2:
            return render_template("signup.html",msg="Enter valid name!")
        elif name.isalpha== False:
            return render_template("signup.html",msg="Enter valid name!")
        elif len(contact)!=10:
            return render_template("signup.html",msg="Enter valid contact number!")
        elif contact.isdigit== False:
            return render_template("signup.html",msg="Enter valid contact number!")
        else:
            if pword1 == pword2:
                password=generate_password_hash(pword1, method='sha256')
                con = None
                try:
                    con = connect("BMI.db")
                    cursor = con.cursor()
                    sql = "insert into signup values('%s','%s','%s','%s','%s')"
                    con.execute(sql % (name, contact, email, username, password))
                    con.commit()
                    msg = Message("Welcome to FitnessGig",
                                sender="fitnessgig123@gmail.com", recipients=[email])
                    msg.body = "“If you want something you’ve never had, you must be willing to do something you’ve never done.” —Thomas Jefferson \n\n Greetings of the day!! \n Welcome " + name + \
                        "\n Thanks for joining FitnessGig. We're excited to have you on board! You've taken the first step towards achieving your fitness goal.\n \n FitnessGig is a one stop fitness center which includes calculation of your BMI and based on that recommendations will be provided.\n\n Hope you are all set to achieve your goal.\n\n Thanks and Regards \n FitnessGig Team "
                    mail.send(msg)
                    return redirect(url_for('login'))
                except Exception:
                    con.rollback()
                    return render_template("signup.html", msg="user already exists")
            else:
                return render_template("signup.html", msg="passwords didnt match")
    else:
        return render_template("signup.html")


@app.route('/index.html')
def indexx():
    return render_template("index.html")


@app.route('/contact.html')
def contact():
    return render_template("contact.html")


@app.route("/bmi.html", methods=['POST', 'GET'])
def calculate():
    bmi = ''    
    if request.method == 'POST':
        height = float(request.form.get('height'))
        weight = float(request.form.get('weight'))
        if weight != '' and height != '':
            bmi = round(weight/((height/100)**2), 2)
            if bmi < 18.5:
                actualweight= round(18.5*((height/100)**2),2)
                msg='''OOPS! 
                You are Underweight! 
                But not to worry,Our Team has some recommendations for maintaining your health.
                Follow the recommendations and regularly check the BMI..Hope you'll have a great time! 
                Thank You
                '''
                
            elif 18.5 <bmi < 24.9 :
                actualweight= 0
                msg='''Great! 
                You are Normal.
                The recommendations prepared by the experts will help you maintain your fitness! 
                Hope you'll have a great time! 
                Thank You'''
            elif 25.0 <bmi < 29.9 :
                actualweight= round(24.9*((height/100)**2),2)
                msg='''OOPS!
                You are Overweight! 
                But not to worry,Our Team has some recommendations for maintaining your health.
                Follow the recommendations and regularly check the BMI..Hope you'll have a great time! 
                Thank You'''
            else:
                actualweight= round(24.9*((height/100)**2),2)
                msg='''OOPS! 
                You are Obessy.
                But not to worry,Our Team has some recommendations for maintaining your health.
                Follow the recommendations and regularly check the BMI..Hope you'll have a great time! 
                Thank You'''
            con = connect("BMI.db")
            cursor = con.cursor()
            sql1="insert into history (username,bmi,weight) values (?, ?, ?);"
            print(username,bmi,weight)
            abc=(username,bmi,weight)
            con.execute(sql1,abc)
            con.commit()
            sql2="select weight from history where username ='%s'"
            cursor.execute(sql2 % (username))
            data = cursor.fetchall()
            data1=data[-1]
            data2 = float('.'.join(str(elem) for elem in data1))
            if actualweight!=0:
                goal=(data2-actualweight)
                if goal>0:
                    goalmsg="GOAL: You have to loose %.2f kgs"%goal
                elif goal==0:
                    goalmsg="Congratulations You have reached your goal!"
                else:
                    goalmsg="GOAL: You have to gain %.2f kgs"%abs(goal)
            else:
                goalmsg="Your are Fit!!"

            chart(a[-1])
            return render_template("rec.html", bmi=bmi,msg=msg,goalmsg=goalmsg)
        else:
            return render_template("bmi.html")
    else:
        return render_template("bmi.html")

if __name__ == '__main__':
    app.run(debug=True, port=5050)
