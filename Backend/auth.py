from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from .db_actions import register_user, verify_user  # relative import

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route("/register", methods=['GET'])
def register_form():
    return render_template('register.html')

@auth_routes.route("/register", methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    fullname = request.form.get('fullname')
    user = register_user(email, password, fullname)
    if user:
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth_routes.login_form'))
    flash("Registration failed. Email may already be in use.", "danger")
    return redirect(url_for('auth_routes.register_form'))

@auth_routes.route("/login", methods=['GET'])
def login_form():
    return render_template('login.html')

@auth_routes.route("/login", methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = verify_user(email, password)
    if user:
        session['user_id'] = user['id']
        session['email'] = user['email']
        flash("Login successful!", "success")
        return redirect(url_for('home'))  # redirect to home or dashboard
    flash("Invalid email or password.", "danger")
    return redirect(url_for('auth_routes.login_form'))
