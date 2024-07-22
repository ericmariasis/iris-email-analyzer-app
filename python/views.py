import os.path
import shutil

from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from .models import *
from .llamaindex import *
views = Blueprint('views', __name__)
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/')
def index():  # put application's code here
    return render_template('index.html', user=current_user)


@views.route('/analyze_email', methods=['GET', 'POST'])
def analyze_email():
    analysis_result = ""
    if request.method == 'POST':
        toEmail = request.form['toEmail'].strip()
        ccEmail = request.form['ccEmail'].strip()
        bccEmail = request.form['bccEmail'].strip()
        message = request.form['message'].strip()

        # Save each form field to a separate text file
        with open('toEmail.txt', 'a') as f_to:
            f_to.write(f"{toEmail}\n")

        with open('ccEmail.txt', 'a') as f_cc:
            f_cc.write(f"{ccEmail}\n")

        with open('bccEmail.txt', 'a') as f_bcc:
            f_bcc.write(f"{bccEmail}\n")

        with open('message.txt', 'a') as f_message:
            f_message.write(f"{message}\n")

            # Ensure the upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        files = []
        if 'attachments' in request.files:
            afiles = request.files.getlist('attachments')
            for file in afiles:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    files.append(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('Email details saved successfully.', 'success')
        companyQ = "Does this look like an email address from outside of a company .com domain?"
        if message:
            analysisAnswer = run_query_on_files(['message.txt'], "Is there anything suspicious in this content? If so what is it? And is there any confidential information provided?")
            analysis_result += "Q: Is there anything suspicious or confidential in the message?\n"
            analysis_result += str(analysisAnswer)
        if toEmail:
            analysis_result += "\n\nQ: Are there any non-company emails listed in the To: field?\n"
            nonCompanyToEmails = run_query_on_files(['toEmail.txt'], companyQ)
            analysis_result += str(nonCompanyToEmails)
        if ccEmail:
            analysis_result += "\n\nQ: Are there any non-company emails listed in the Cc: field?\n"
            nonCompanyCcEmails = run_query_on_files(['ccEmail.txt'], companyQ)
            analysis_result += str(nonCompanyCcEmails)
        if bccEmail:
            analysis_result += "\n\nQ: Are there any non-company emails listed in the Bcc: field?\n"
            nonCompanyBccEmails = run_query_on_files(['bccEmail.txt'], companyQ)
            analysis_result += str(nonCompanyBccEmails)
        if len(files) > 0:
            analysis_result += "\n\nQ: Is there anything suspicious or confidential in the uploaded attachments?\n"
            attachmentAnswer = run_query_on_files(files, "Is there anything suspicious in this content? If so what is it? And is there anything confidential?")
            analysis_result += str(attachmentAnswer)
        # Pass the form data back to the template
        response = render_template('analyze_email.html', user=current_user, toEmail=toEmail, ccEmail=ccEmail,
                               bccEmail=bccEmail, message=message, analysis_result=analysis_result)
        toDelete = ['message.txt', 'toEmail.txt', 'ccEmail.txt', 'bccEmail.txt']
        for file in toDelete:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                print("Error deleting", file, ": {e}")
        # Delete the contents of the upload directory
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        return response

    # Render the form with empty fields on GET request
    return render_template('analyze_email.html', user=current_user, toEmail='', ccEmail='', bccEmail='', message='', analysis_result=analysis_result)

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
