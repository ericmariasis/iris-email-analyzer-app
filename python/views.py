from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from python.forms import SignupForm
from .models import *
from .myconfig import *
views = Blueprint('views', __name__)
app = Flask(__name__)


@views.route('/')
def index():  # put application's code here
    return render_template('index.html', user=current_user)


@views.route('/analyze_email')
def analyze_email():
    return render_template('analyze_email.html', user=current_user)

@views.route('/roles')
def roles():
    return render_template('roles.html', user=current_user)


@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('User does not exist.', category='error')
    return render_template('login.html', user=current_user)


@views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('You are now logged in.', category='success')
            return redirect(url_for('views.login'))
    return render_template('signup.html', user=current_user)

@views.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.index"))


if __name__ == '__main__':
    app.run(debug=True)
