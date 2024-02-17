from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://abi:1@HCUS19WS066/ApiDb?driver=ODBC+Driver+18+for+SQL+Server&encrypt=no'
# SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://abi:1@HCUS19WS066/ApiDb?driver=ODBC+Driver+18+for+SQL+Server'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Define SQLAlchemy models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)  # Increased maximum length to 100 characters
    password_hash = db.Column(db.String(
        
    ), nullable=False) # ==> NVARCHAR(MAX)
    role = db.Column(db.String(20), nullable=False)

    
    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)
    
def create_tables():
    with app.app_context():
        try:
            db.create_all()
            print("Tables created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")

# Function to hash passwords
def hash_password(password):
    return generate_password_hash(password)


# Define routes
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    role = request.json.get('role', 'user')  # Default role is 'user'

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    # user = User(username=username, password=password, role=role)
    # db.session.add(user)
    # db.session.commit()
    hashed_password = hash_password(password)
    new_user = User(username=username, password_hash=hashed_password, role=role)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"msg": f"Error creating user: {e}"}), 500

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
    return jsonify(access_token=access_token), 200

# Protected route example
# @app.route('/protected', methods=['GET'])
# @jwt_required()
# def protected():
#     current_user = get_jwt_identity()
#     user_role = get_jwt_claims()['role']
#     return jsonify(logged_in_as=current_user, role=user_role), 200

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
