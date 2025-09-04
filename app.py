from flask import Flask, render_template
from Backend.db import get_db_connection
from Backend.auth import auth_routes
import Backend.db_actions as db_actions


def create_app():
    app = Flask(__name__)
    app.secret_key = "your_secret_key"

    db_actions.init_user_table()

    app.register_blueprint(auth_routes)
    return app

app = create_app()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)