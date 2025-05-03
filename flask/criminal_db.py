from trikon import app, db, Criminal
from trikon import Criminal  

with app.app_context():
    db.create_all()
    
