from crypt import methods
from flask import Flask,render_template,redirect,url_for,request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename
from pytz import timezone
import os


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///userdb.db"
app.config["SQLALCHEMY_BINDS"] = {
    "RepoDB": "sqlite:///repodb.db",
    "FileDB": "sqlite:///filedb.db",
    "AppointmentDB": "sqlite:///appointmentdb.db",
    "prescriptionDB":"sqlite:///prescriptiondb.db"
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "/Users/bhuvanm/Desktop/miniproject/static/files"
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

class RepoDB(db.Model):
    __bind_key__ = 'RepoDB'
    id = db.Column(db.Integer, primary_key=True)
    userN = db.Column(db.String(20),nullable=False)
    nameOfRepo = db.Column(db.String(50),nullable = False)
    dateCreated = db.Column(db.String(30),default=datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S.%f'))

    def __repr__(self) -> str:
        return f"{self.id}"

class FileDB(db.Model):
    __bind_key__ = "FileDB"
    id = db.Column(db.Integer, primary_key=True)
    userAndRepoName = db.Column(db.String(100),nullable=False)
    fileName = db.Column(db.Text,nullable=False)
    name = db.Column(db.String(50),nullable=False)
    desc = db.Column(db.String(200))
    mimetype = db.Column(db.Text,nullable=False)

class AppointmentDB(db.Model):
    __bind_key__ = "AppointmentDB"
    id = db.Column(db.Integer, primary_key=True)
    userN = db.Column(db.String(100),nullable=False)
    doctorN = db.Column(db.String(100),nullable=False)
    hospitalN = db.Column(db.String(100),nullable=False)
    date = db.Column(db.String(15),nullable=False)
    time = db.Column(db.String(10),nullable=False)

class prescriptionDB(db.Model):
    __bind_key__ = "prescriptionDB"
    id = db.Column(db.Integer, primary_key=True)
    userN = db.Column(db.String(100),nullable=False)
    medN = db.Column(db.String(100),nullable=False)
    freq = db.Column(db.String(100),nullable=False)
    duration = db.Column(db.String(30),nullable=False)


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
            if userpwd != request.form["cp"]:
                return render_template("register.html",x=3)
            hashed_userpwd = bcrypt.generate_password_hash(userpwd,14)
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
    repos = RepoDB.query.filter_by(userN=uName).all()
    return render_template("profile.html",user=user,repos=repos)

@app.route("/profile/<string:uName>/editProfile",methods=["GET","POST"])
def editProfile(uName):
    if request.method == "POST":
        prof = UserDB.query.filter_by(userName=uName).first()
        prof.userFirstName = request.form["upfn"]
        prof.userLastName = request.form["upln"]
        prof.userEmailID = request.form["upeid"]
        prof.userDOB = request.form["updob"]
        db.session.add(prof)
        db.session.commit()
        return redirect(f"/profile/{uName}")
    prof = UserDB.query.filter_by(userName=uName).first()
    return render_template("editProfile.html",username=uName,prof=prof)

@app.route("/profile/<string:uName>/editProfile/changePWD",methods=["GET","POST"])
def changePWD(uName):
    if request.method == "POST":
        prof = UserDB.query.filter_by(userName=uName).first()
        if not bcrypt.check_password_hash(prof.userPassword, request.form["pucp"]):
            return render_template("changePwd.html",username=uName,x=1)
        else:
            prof.userPassword = bcrypt.generate_password_hash(request.form["punp"],14)
            db.session.add(prof)
            db.session.commit()
            return render_template("changePwd.html",username=uName,x=2)
    return render_template("changePwd.html",username=uName)


@app.route("/profile/<string:uName>/createrepo",methods=["GET","POST"])
def createRepo(uName):
    if request.method == "POST":
        repo = RepoDB(userN=uName,nameOfRepo=request.form["rn"])
        db.session.add(repo)
        db.session.commit()
        return redirect(f"/profile/{uName}")
    return render_template("createRepo.html",username=uName)

@app.route("/profile/<string:uName>/<int:repoID>")
def repo(uName,repoID):
    files = FileDB.query.filter_by(userAndRepoName=uName+str(repoID)).all()
    return render_template("repo.html",username=uName,repoID=repoID,files=files)

@app.route("/profile/<string:uName>/<int:repoID>/upload",methods=["GET","POST"])
def fileUpload(uName,repoID):
    File = request.files["file"]
    
    fName = File.filename.split(".")
    File.filename = fName[0]+ uName + str(datetime.now()) + "." + fName[1]
    fName = secure_filename(File.filename)
    File.save(os.path.join(app.config["UPLOAD_FOLDER"],fName))
    mimetype = File.mimetype
    file = FileDB(userAndRepoName=uName+str(repoID),fileName=fName,name=request.form["fileName"],desc=request.form["fileDesc"],mimetype=mimetype)
    db.session.add(file)
    db.session.commit()
    return redirect(f"/profile/{uName}/{repoID}")

@app.route("/profile/<string:uName>/appointment")
def appointment(uName):
    appos = AppointmentDB.query.filter_by(userN=uName).all()
    return render_template("appointment.html",username=uName,appos=appos)

@app.route("/profile/<string:uName>/appointment/createAppointment",methods=["GET","POST"])
def createAppointment(uName):
    if request.method == "POST":
        dn = request.form["dname"]
        hn = request.form["hname"]
        t = request.form["atime"]
        d = request.form["adate"]
        appo = AppointmentDB(userN=uName,doctorN=dn,hospitalN=hn,date=str(d),time=str(t))
        db.session.add(appo)
        db.session.commit()
        return redirect(f"/profile/{uName}/appointment")
    return render_template("createAppointment.html",username=uName)

@app.route("/profile/<string:uName>/<int:appoID>/appoupdate",methods=["GET","POST"])
def appointmentUpdate(uName,appoID):
    if request.method == "POST":
        appo = AppointmentDB.query.filter_by(id=appoID).first()
        appo.doctorN = request.form["audn"]
        appo.hospitalN = request.form["auhn"]
        appo.time = str(request.form["autime"])
        appo.date = str(request.form["audate"])
        db.session.add(appo)
        db.session.commit()
        return redirect(f"/profile/{uName}/appointment")
    appo = AppointmentDB.query.filter_by(id=appoID).first()
    return render_template("appoUpdate.html",username=uName,aID=appoID,appo=appo)

@app.route("/profile/<string:uName>/<int:appoID>/appodelete")
def appointmentDelete(uName,appoID):
    appo = AppointmentDB.query.filter_by(id=appoID).first()
    db.session.delete(appo)
    db.session.commit()
    return redirect(f"/profile/{uName}/appointment")


@app.route("/profile/<string:uName>/prescription")
def prescription(uName):
    pers = prescriptionDB.query.filter_by(userN=uName).all()
    return render_template("prescription.html",username=uName,pers=pers)

@app.route("/profile/<string:uName>/prescription/createPrescription",methods=["GET","POST"])
def createPrescription(uName):
    if request.method == "POST":
        medname = request.form["pmname"]
        pfreq = request.form.getlist("pfreq")
        pd = request.form["pdur"]
        st = ""
        for x in pfreq:
            st += x
            st+=","
        per = prescriptionDB(userN=uName,medN=medname,freq=st[:-1],duration = pd)
        db.session.add(per)
        db.session.commit()
        return redirect(f"/profile/{uName}/prescription")
    return render_template("createPrescription.html",username=uName)

@app.route("/profile/<string:uName>/<int:perID>/perupdate",methods=["GET","POST"])
def updatePrescription(uName,perID):
    if request.method == "POST":
        per = prescriptionDB.query.filter_by(id=perID).first()
        per.medN = request.form["pumname"]
        pfreq = request.form.getlist("pufreq")
        per.duration = request.form["pudur"]
        st = ""
        for x in pfreq:
            st += x
            st+=","
        per.freq = st[:-1]
        db.session.add(per)
        db.session.commit()
        return redirect(f"/profile/{uName}/prescription")
    per = prescriptionDB.query.filter_by(id=perID).first()
    return render_template("persUpdate.html",username=uName,perID=perID,per=per)

@app.route("/profile/<string:uName>/<int:perID>/perdelete")
def persDelete(uName,perID):
    per = prescriptionDB.query.filter_by(id=perID).first()
    db.session.delete(per)
    db.session.commit()
    return redirect(f"/profile/{uName}/prescription")

@app.route("/profile/<string:uName>/<int:repoID>/repodelete")
def repoDelete(uName,repoID):
    file = FileDB.query.filter_by(userAndRepoName=uName+str(repoID)).all()
    for f in file:
        fl = FileDB.query.filter_by(id=f.id).first()
        db.session.delete(fl)
        db.session.commit()
    repo = RepoDB.query.filter_by(id=repoID).first()
    db.session.delete(repo)
    db.session.commit()
    return redirect(f"/profile/{uName}")

@app.route("/profile/<string:uName>/<int:repoID>/repoupdate",methods=["GET","POST"])
def repoUpdate(uName,repoID):
    if request.method == "POST":
        newName = request.form["run"]
        rep = RepoDB.query.filter_by(id=repoID).first()
        rep.nameOfRepo = newName
        db.session.add(rep)
        db.session.commit()
        return redirect(f"/profile/{uName}")
    repo = RepoDB.query.filter_by(id=repoID).first()
    return render_template("repoUpdate.html",username=uName,repoID=repoID,repo=repo)

@app.route("/profile/<string:uName>/<int:repoID>/<int:fileID>/filedelete")
def fileDelete(uName,repoID,fileID):
    file = FileDB.query.filter_by(id=fileID).first()
    db.session.delete(file)
    db.session.commit()
    return redirect(f"/profile/{uName}/{repoID}")

@app.route("/profile/<string:uName>/<int:repoID>/<int:fileID>/fileupdate",methods=["GET","POST"])
def fileUpdate(uName,repoID,fileID):
    if request.method == "POST":
        file = FileDB.query.filter_by(id=fileID).first()
        file.name = request.form["fut"]
        file.desc = request.form["fud"]
        db.session.add(file)
        db.session.commit()
        return redirect(f"/profile/{uName}/{repoID}")
    file = FileDB.query.filter_by(id=fileID).first()
    return render_template("fileUpdate.html",username=uName,repoID=repoID,fileID=fileID,file=file)

@app.route("/profile/<string:uName>/diseasedetection")
def diseaseDetection(uName):
    return render_template("diseaseDetection.html")


if __name__ == "__main__":
    app.run(debug=True)