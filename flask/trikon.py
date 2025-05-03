from flask import Flask , render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///criminal.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER']=os.path.join(os.getcwd(),'static')
app.config['ALLOWED_EXTENSIONS']=set(['png', 'jpg', 'jpeg' ])
db=SQLAlchemy(app)

class Criminal(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    image_file=db.Column(db.String(100), default='default.jpg')
    name=db.Column(db.String(50), nullable=False)
    fatherName=db.Column(db.String(50), nullable=False)
    dob=db.Column(db.Date, nullable=False)
    address=db.Column(db.String(100), nullable=False)
    number=db.Column(db.Integer, nullable=False)
    crimeDate=db.Column(db.Date, nullable=False)
    crimeDesc=db.Column(db.String(200), nullable=False)
    email=db.Column(db.String(100), nullable=False)
    date_registered=db.Column(db.DateTime , default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno}-{self.name}"  
    

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    if request.method=='POST':
        file=request.files['image_file']
        name=request.form['name']
        fatherName=request.form['fatherName']
        dob=request.form['dob']
        address=request.form['address']
        number=request.form['number']
        crimeDate=request.form['crimeDate']
        crimeDesc=request.form['crimeDesc']
        email=request.form['email']
        crime_date = datetime.strptime(crimeDate, "%Y-%m-%d").date()
        dob_t = datetime.strptime(dob, "%Y-%m-%d").date()
    
        if file and allowed_file(file.filename):
            filename=file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename='default.jpg'

        criminal=Criminal(image_file=filename, name=name, fatherName=fatherName, dob=dob_t, address=address, number=number, crimeDate=crime_date, crimeDesc=crimeDesc, email=email)

        db.session.add(criminal)
        db.session.commit()
        return redirect(url_for('hello_world'))
    allcriminals=Criminal.query.all()
    
    return render_template('index.html', allcriminals=allcriminals)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/delete/<int:sno>')
def delete(sno):
    criminal=Criminal.query.filter_by(sno=sno).first()
    db.session.delete(criminal)
    db.session.commit()
    return redirect('/')

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method=='POST':
        file=request.files['image_file']
        name=request.form['name']
        fatherName=request.form['fatherName']
        dob=request.form['dob']
        address=request.form['address']
        number=request.form['number']
        crimeDate=request.form['crimeDate']
        crimeDesc=request.form['crimeDesc']
        email=request.form['email']
        crime_date = datetime.strptime(crimeDate, "%Y-%m-%d").date()
        dob_t = datetime.strptime(dob, "%Y-%m-%d").date()

        if file and allowed_file(file.filename):
            filename=file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename='default.jpg'

        criminal=Criminal.query.filter_by(sno=sno).first()

        criminal.image_file=filename
        criminal.name=name
        criminal.fatherName=fatherName
        criminal.dob=dob_t
        criminal.address=address
        criminal.number=number
        criminal.crime_date=crime_date
        criminal.crimeDesc=crimeDesc
        criminal.email=email


        db.session.add(criminal)
        db.session.commit()
        return redirect('/')
    

    criminal=Criminal.query.filter_by(sno=sno).first()
    return render_template('update.html', criminal=criminal)

if __name__== "__main__":

    with app.app_context():
        db.create_all()  
    app.run(debug=True)