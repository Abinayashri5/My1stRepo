from flask import Flask, jsonify, request
import sqlalchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity