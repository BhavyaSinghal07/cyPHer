from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)

# ————— CONFIGURATION —————
app.config['SQLALCHEMY_DATABASE_URI']        = "sqlite:///criminal.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Base directory of this script
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Store uploads in static/uploads
UPLOAD_SUBFOLDER = 'uploads'
UPLOAD_FOLDER    = os.path.join(BASE_DIR, 'static', UPLOAD_SUBFOLDER)
ALLOWED_EXTS     = {'png', 'jpg', 'jpeg'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTS

db = SQLAlchemy(app)

# ————— DATABASE MODEL —————
class Criminal(db.Model):
    sno             = db.Column(db.Integer, primary_key=True)
    image_file      = db.Column(db.String(200), default='default.jpg')
    name            = db.Column(db.String(50),  nullable=False)
    fatherName      = db.Column(db.String(50),  nullable=False)
    dob             = db.Column(db.Date,        nullable=False)
    address         = db.Column(db.String(100), nullable=False)
    number          = db.Column(db.Integer,     nullable=False)
    crimeDate       = db.Column(db.Date,        nullable=False)
    crimeDesc       = db.Column(db.String(200), nullable=False)
    email           = db.Column(db.String(100), nullable=False)
    date_registered = db.Column(db.DateTime,    default=datetime.utcnow)

    def __repr__(self):
        return f"<Criminal {self.sno} – {self.name}>"

# ————— HELPERS —————
def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    )

def handle_file_upload(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return 'default.jpg'

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()

# ————— ROUTES —————
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        try:
            filename = handle_file_upload(request.files.get('image_file'))
            
            new_criminal = Criminal(
                image_file=filename,
                name=request.form['name'],
                fatherName=request.form['fatherName'],
                dob=parse_date(request.form['dob']),
                address=request.form['address'],
                number=int(request.form['number']),
                crimeDate=parse_date(request.form['crimeDate']),
                crimeDesc=request.form['crimeDesc'],
                email=request.form['email']
            )
            db.session.add(new_criminal)
            db.session.commit()
            return redirect(url_for('hello_world'))
        except Exception as e:
            db.session.rollback()
            # In a production app, you'd want to log the error and show a user-friendly message
            return str(e), 400

    allcriminals = Criminal.query.all()
    return render_template(
        'dashboard.html',
        allcriminals=allcriminals,
        upload_subfolder=UPLOAD_SUBFOLDER
    )

@app.route('/delete/<int:sno>')
def delete(sno):
    try:
        criminal = Criminal.query.get_or_404(sno)
        if criminal.image_file != 'default.jpg':
            # Delete the associated image file
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], criminal.image_file)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(criminal)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return str(e), 400
    return redirect(url_for('hello_world'))

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    criminal = Criminal.query.get_or_404(sno)

    if request.method == 'POST':
        try:
            file = request.files.get('image_file')
            if file:
                filename = handle_file_upload(file)
                if filename != 'default.jpg':
                    # Delete old image if it exists and isn't the default
                    if criminal.image_file != 'default.jpg':
                        old_image = os.path.join(app.config['UPLOAD_FOLDER'], criminal.image_file)
                        if os.path.exists(old_image):
                            os.remove(old_image)
                    criminal.image_file = filename

            criminal.name = request.form['name']
            criminal.fatherName = request.form['fatherName']
            criminal.dob = parse_date(request.form['dob'])
            criminal.address = request.form['address']
            criminal.number = int(request.form['number'])
            criminal.crimeDate = parse_date(request.form['crimeDate'])
            criminal.crimeDesc = request.form['crimeDesc']
            criminal.email = request.form['email']

            db.session.commit()
            return redirect(url_for('hello_world'))
        except Exception as e:
            db.session.rollback()
            return str(e), 400

    return render_template(
        'update.html',
        criminal=criminal,
        upload_subfolder=UPLOAD_SUBFOLDER
    )

# ————— APP LAUNCH —————
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)