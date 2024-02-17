from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this to your preferred secret key
jwt = JWTManager(app)

# Defining SQL Server connection details
server = 'HCUS19WS066'
database = 'DbF'
username = 'Abi'
password = '1'

# Creating the SQLAlchemy engine
engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server&encrypt=no')

# Creating a session class
Session = sessionmaker(bind=engine)

# Creating a base class
Base = declarative_base()

# Define the Book model
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)

# Create the tables
Base.metadata.create_all(engine)

# API endpoints

# Login endpoint to generate JWT token
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') != 'admin' or data.get('password') != 'admin':  # Change to your actual authentication logic
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=data.get('username'))
    return jsonify(access_token=access_token), 200

# Protected endpoint using JWT
@app.route('/books', methods=['GET'])
@jwt_required()
def get_all_books():
    session = Session()
    books = session.query(Book).all()
    session.close()
    return jsonify([book.__dict__ for book in books])

# Other endpoints...

if __name__ == '__main__':
    app.run(debug=True)
