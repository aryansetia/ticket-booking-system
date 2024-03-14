from flask import Blueprint, request, jsonify, session
from app.models.admin import Admin 

login_api = Blueprint('login_api', __name__)

@login_api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    admin = Admin.query.filter_by(username=username).first()

    if not admin or not admin.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401

    # Set admin_logged_in session variable upon successful login
    session['admin_logged_in'] = True
    return jsonify({'message': 'Login successful'}), 200


@login_api.route('/logout', methods=['POST'])
def logout():
    # Remove admin_logged_in session variable upon logout
    session.pop('admin_logged_in', None)
    return jsonify({'message': 'Logged out successfully'}), 200
