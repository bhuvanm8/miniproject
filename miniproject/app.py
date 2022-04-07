from crypt import methods
import bcrypt
from flask import Flask,render_template,redirect,url_for,request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class UserDB(db.Model):
    userName = db.Column(db.String(20),primary_key=True)
    userPassword = db.Column(db.String(100),nullable=False)
    userFirstName = db.Column(db.String(50),nullable=False)
    userLastName = db.Column(db.String(50),nullable=False)
    userEmailID = db.Column(db.String(100),nullable=False)
    userDOB = db.Column(db.String(20),nullable=False)

    def __repr__(self) -> str:
        return f"{self.userName}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        if UserDB.query.filter_by(userName=request.form["un"]).first() is None:
            usern = request.form["un"]
            userpwd = request.form['up']
            usereid = request.form["ueid"]
            userdob = request.form["udob"]
            userfn = request.form["ufn"]
            userln = request.form["uln"]
            hashed_userpwd = bcrypt.generate_password_hash(userpwd)
            user = UserDB(userName=usern,userPassword=hashed_userpwd,userFirstName=userfn,userLastName=userln,userEmailID=usereid,userDOB=userdob)
            db.session.add(user)
            db.session.commit()
            return render_template("register.html",x=2)
        return render_template("register.html",x=1)
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        usern = request.form["una"]
        if UserDB.query.filter_by(userName=usern).first() is not None:
            userpwd = request.form['upa']
            if bcrypt.check_password_hash(UserDB.query.filter_by(userName=usern).first().userPassword, userpwd):
                return redirect(f"/profile/{usern}")
            else:
                return render_template("login.html",x=1)
        else:
            return render_template("login.html",x=1)

        
    return render_template("login.html")

@app.route("/profile/<string:uName>")
def profile(uName):
    user = UserDB.query.filter_by(userName=uName).first()
    return render_template("profile.html",user=user)

if __name__ == "__main__":
    app.run(debug=True)