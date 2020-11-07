#big time website yo
import pymysql
import os
from werkzeug.utils import secure_filename

#--------------- SQL SETUPAND FUNCS -------------------------------------------------#
connection = pymysql.connect(host="localhost",user="root",password="password",db='webApp')

curs = connection.cursor()
#curs.execute("""INSERT INTO productlist values("004","Sharpeners",5,1.00)""")
#connection.commit()

def checkUname(uname,fname,lname):
    try:
        curs.execute("""INSERT INTO userData VALUES(%s,%s,%s)""",(uname,fname,lname))
        connection.commit()
        return True
    except:
        return False

def getUserData(userName):
    curs.execute("""SELECT * FROM userData WHERE uname = %s; """,(userName))
    data = curs.fetchall()
    dataDic = {'User Name':data[0][0],'First Name':data[0][1],'Last Name':data[0][2],'Gender':data[0][3]}
    return dataDic

def getUserPic(userName):
    try:
        curs.execute("""SELECT * FROM userPics WHERE uname = %s; """,(userName))
        data = curs.fetchall()
        dataP = data[0][1]
    except:
        dataP = 'default.jpg'
    return dataP


def getAll():
    curs.execute("""SELECT * FROM userData;""")
    data = curs.fetchall()
    return data

def getChats():
    curs.execute("""SELECT * FROM userChat;""")
    data = curs.fetchall()
    return data

def sord(uname,chat):
    #submit or update
    curs.execute("""SELECT EXISTS(SELECT * FROM userChat WHERE uname = %s)""",(uname))
    val = curs.fetchall()[0][0]
    if val == 0:
        curs.execute("""INSERT INTO userChat VALUES(%s,%s)""",(uname,chat))
        connection.commit()
    if val == 1:
        curs.execute("""UPDATE userChat SET chat = %s WHERE uname = %s;""",(chat,uname))
        connection.commit()

#--------------- SQL SETUPAND FUNCS -------------------------------------------------#


#--------------- FLASK SETUP -------------------------------------------------#
from flask import Flask, redirect, render_template, url_for, request, make_response
app = Flask(__name__, static_folder = "static")
app.config["IMAGE_UPLOADS"] = '/home/ec2-user/website_alpha_v2/static/userpics'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
#--------------- FLASK SETUP -------------------------------------------------#


#--------------- APP ROUTES -------------------------------------------------#
def isCookie():
    try:
        banana = request.cookies.get('userID')

        if banana is None :
            return False
        else: return True

        return True
    except:
        return False

def allowed_image(filename):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

@app.route('/isCookie_test/')
def cookietest():
    banana = request.cookies.get('userID')
    if isCookie():
        y = 'yes' + banana
        return y
    else: return ('no')

def lilTest():
    return 'This is a website...\n:)'

@app.route('/')
def hi():
   if isCookie():
       return redirect(url_for('homeUser'))

   else: return redirect(url_for('homeGuest'))


@app.route('/home/')
def welcome():
    return redirect(url_for('hi'))

@app.route('/signup/')
def signup():
    return render_template('signUpForm.html')

@app.route('/login',methods = ['POST'])
def login():
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['password']
        fname = request.form['fname']
        lname = request.form['lname']
        try:
            gen = request.form['gender']
        except:
            gen = 'other'
        curs.execute("""INSERT INTO userData VALUES(%s,%s,%s,%s,%s)""",(uname,fname,lname,gen,pwd))
        connection.commit()
        #imagename = request.form['image']
        try:
            image = request.files['image']
            if image.filename == "":
                #print("No filename")
                curs.execute("""INSERT INTO userPics VALUES(%s,%s)""",(uname,'default.jpg'))
                connection.commit()
            if allowed_image(image.filename):
                filename = secure_filename(image.filename)
                #image.save(image.filename)
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
                curs.execute("""INSERT INTO userPics VALUES(%s,%s)""",(uname,image.filename))
                connection.commit()
        except:
            curs.execute("""INSERT INTO userPics VALUES(%s,%s)""",(uname,'default.jpg'))
            connection.commit()

        user = request.form['uname']

        resp = make_response(redirect(url_for('hi')))
        resp.set_cookie('userID', user)
        #return redirect(url_for(thanks(userf)))
        return resp

@app.route('/welcome_back/')
def backAgain():
    return render_template('returnForm.html')

@app.route('/logback/',methods = ['POST'])
def logback():
    if request.method == 'POST':
        user = request.form['uname']
        pwd = request.form['password']
        curs.execute("""SELECT EXISTS(SELECT * FROM userData WHERE uname = %s AND password = %s)""",(user,pwd))
        val = curs.fetchall()[0][0]
        print(val)
        if val:
            print(val)
            resp = make_response(redirect(url_for('hi')))
            resp.set_cookie('userID', user)
            #return redirect(url_for(thanks(userf)))
            return resp
        else: return (redirect(url_for('backAgain')))

@app.route('/thank_you/')
def thanks():
    idname = request.cookies.get('userID')
    data = getUserData(idname)
    return 'Thank you for signing up %s %s: %s' %(data['First Name'].title(),data['Last Name'].title(),idname)

#datadic = {'First Name':data[0],'Last Name':data[1]}
@app.route('/profile/')
def profile():
    userName = request.cookies.get('userID')
    userDic = getUserData(userName)
    picloc = getUserPic(userName)
    return render_template("profilepage.html",data = userDic, pic = picloc)

@app.route('/profile/<name>')
def profileother(name):
    userName = name
    userDic = getUserData(userName)
    picloc = getUserPic(userName)
    return render_template("profilepageother.html",data = userDic, pic = picloc,uname=name)

@app.route('/all/')
def all():
    #userName = request.cookies.get('userID')
    alldata = getAll()
    return render_template("allprofilepage.html",data = alldata)

@app.route('/homeuser/')
def homeUser():
    userName = request.cookies.get('userID')
    data = getChats()
    #pic = getUserPic(userName)
    return render_template('homeUser.html',data=data,userName=userName)


@app.route('/addchat/',methods = ['POST'])
def addChat():
    if request.method == 'POST':
        chatter = request.form['chatter']
        userName = request.cookies.get('userID')
        #curs.execute("""INSERT INTO userChat VALUES(%s,%s)""",(userName,chatter))
        #connection.commit()
        sord(userName,chatter)
        return redirect(url_for('homeUser'))
        #return 'done'

@app.route('/homeguest/')
def homeGuest():
    data = getChats()
    return render_template('homeGuest.html',data=data)

@app.route('/directhome1/',methods = ['POST'])
def directHome1():
    if request.method == 'POST':
        return redirect(url_for('signup'))

@app.route('/directhome2/',methods = ['POST'])
def directHome2():
    if request.method == 'POST':
        return redirect(url_for('backAgain'))

@app.route('/sign-out/')
def signOut():
    userName = request.cookies.get('userID')
    res = make_response(redirect(url_for('hi')))
    res.set_cookie('userID', userName, max_age=0)
    return res

@app.route('/about/')
def about():
    return render_template('about.html')

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=80)

connection.close()
