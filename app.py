from flask import Flask,request,redirect,url_for,render_template,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_required,current_user,logout_user,login_user
from datetime import datetime


#initialize the app
app = Flask(__name__)

#app config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db" 
app.config["SECRET_KEY"] = 'UltraMegaSecretiveKey69'
#initialize the db
db = SQLAlchemy(app)

#initialize login
login_manager = LoginManager()
login_manager.init_app(app)

#Model
"""
This class handles the model of databse for books 

columns are id,bookName,author,isBorrowed,borrowedBy,
dateBorrowed, dateReturned,dateRegistered
"""
class Books(db.Model):
    #Book Model
    id = db.Column(db.Integer,primary_key = True)
    bookName = db.Column(db.String(100), nullable = False)
    author = db.Column(db.String(50), nullable = False)
    isBorrowed = db.Column(db.Boolean, nullable = True)
    borrowedBy = db.Column(db.String(30), nullable = True)
    dateBorrowed = db.Column(db.DateTime, nullable = True)
    dateReturned = db.Column(db.DateTime,nullable=True)
    dateRegistered = db.Column(db.DateTime, nullable = False, default = datetime.now())



class Users(UserMixin, db.Model):
    #User Model
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True, nullable = False)
    password = db.Column(db.String(30), nullable = False)

# Flask_Login loader
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


#functions 
"""
this function takes care of login function by users
this checks if user is able to provide necessary information
"""

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username, password=password).first()
        if user is not None:
            login_user(user)
            return redirect(url_for('indexPage'))
        else:
            flash('Login Error, Please try again',category="'error'")
            return redirect(url_for('login'))

    else:
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/createAccount',methods=['POST','GET'])
def makeAccount():
    if request.method == "GET":
        if current_user.is_authenticated == True:
            return redirect(url_for('indexPage'))
        else:
            return render_template('createAccount.html')
    else:
        try:
            newUsername = request.form.get('username')
            newPassword = request.form.get('password')
            user = Users(username=newUsername,password=newPassword)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            flash("Username Taken!", "'error'")
            return redirect(url_for('makeAccount'))

@app.route('/')
def indexPage():
    
    if current_user.is_authenticated == False:
        return redirect(url_for("login"))
    else:
        return render_template("index.html",title='Home')

@app.route('/borrow',methods=['POST','GET'])
@login_required
def borrowBooks():
    if request.method == "GET":
        contents = Books.query.filter_by(isBorrowed=False).order_by(Books.bookName).all()
        return render_template('borrow.html',contents=contents)
    else:
        reqbook = request.form.get('borrow_btn')
        book = Books.query.filter_by(bookName=reqbook).first()
        if book.isBorrowed == False:
            book.isBorrowed = True
            book.borrowedBy = current_user.username
            book.dateBorrowed = datetime.now()
            db.session.commit()
            return redirect(url_for('borrowBooks'))
        else:
            flash('currently borrowed, please choose another!','error')
            return redirect(url_for('borrowBooks'))

@app.route('/return',methods=['POST','GET'])
@login_required
def returnBooks():
    
    if request.method == "POST":
        reqBook=request.form.get('return_btn')
        book = Books.query.filter_by(bookName=reqBook).first()
        if book.isBorrowed == True and current_user.username == book.borrowedBy:
            book.isBorrowed = True
            book.dateReturned = datetime.now()
            db.session.commit()
            return redirect(url_for('returnBooks'))
        else:
            flash("User and Recorded borrower doesn't match",'error')
            return redirect(url_for('returnBooks'))
    else:
        return render_template('return.html')




@app.route('/add',methods=['POST','GET'])
@login_required
def addBooks():
    if request.method == 'POST':
        pass
    else:
        return render_template('add.html')

@app.route('/delete',methods=['POST'])
@login_required
def deleteBooks():
    pass