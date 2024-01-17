from flask import Flask, render_template, request, flash, redirect, url_for, session, g, abort
from pymongo import MongoClient
from forms import ContactForm, RegistrationForm, LoginForm
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

mail = Mail()

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.getenv('MAIL_USERNAME')
app.config["MAIL_PASSWORD"] = os.getenv('MAIL_PASSWORD')
app.config["MONGO_URI"] = os.getenv('MONGO_URI')

mail.__init__(app)


def get_mongo_client():
    if 'mongo_client' not in g:
        g.mongo_client = MongoClient(app.config["MONGO_URI"])
    return g.mongo_client

def get_user_collection():
    db = get_mongo_client().apartments
    return db.users

def get_tenants_collection():
    db = get_mongo_client().apartments
    return db.tenants

def get_chat_collection():
    db = get_mongo_client().apartments
    return db.chat

@app.route("/")
def home():
    with get_mongo_client() as client:
        db = client.apartments
        news_collection = db.news
        all_news = list(news_collection.find())
    return render_template("home.html", news=all_news)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    with get_mongo_client() as client:
        db = client.apartments
        news_collection = db.news
        all_news = list(news_collection.find().limit(3))

    if request.method == 'POST':
        if form.validate():
            msg = Message(form.subject.data, sender='contact@example.com', recipients=['itykutyku@gmail.com'])
            msg.body = f"From: {form.name.data} <{form.email.data}>\n{form.message.data}"
            mail.send(msg)
            return render_template('contact.html', success=True, form=form, news=all_news)
        else:
            flash('All fields are required.')

    return render_template('contact.html', form=form, news=all_news)

@app.route("/energy")
def energy():
    return render_template('energy.html')

@app.route("/group", methods=['GET', 'POST'])
def group():
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            username = session['user']['username']
            chat_collection = get_chat_collection()
            chat_collection.insert_one({'username': username, 'message': message})

    # Retrieve the last 5 messages from the chat collection
    chat_collection = get_chat_collection()
    messages = list(chat_collection.find().sort('_id', -1).limit(15))[::-1]

    return render_template('group.html', messages=messages)


@app.route("/tenant")
def tenant():
    if 'user' in session:
        tenants_collection = get_tenants_collection()
        tenant_info = tenants_collection.find_one({'email': session['user']['email']})

        return render_template('tenant.html', tenants_collection=tenants_collection, tenant=tenant_info)
    else:
        return render_template('tenant.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'POST' and form.validate():
        with get_mongo_client() as client:
            db = client.apartments
            users_collection = db.users

            # Check if the user already exists
            if users_collection.find_one({'email': form.email.data}):
                flash('Email address is already registered.')
                return render_template('register.html', form=form)

            # Add the user to the database (hash the password in production)
            result = users_collection.insert_one({
                'username': form.username.data,
                'email': form.email.data,
                'password': form.password.data,  # Note: In production, hash the password
            })

            if result.inserted_id:
                flash('Registration successful. You can now log in.')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please try again.')

    return render_template('register.html', form=form)

from flask import request

@app.route('/profile')
def profile():
    # Check if the user is logged in
    if 'user' not in session:
        flash('Login required', 'danger')
        return redirect(url_for('login'))

    # Fetch user information from the session
    user_info = session['user']

    return render_template('profile.html', user=user_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data

        user_collection = get_user_collection()
        user = user_collection.find_one({'email': email, 'password': password})

        if user:
            # Store user information in the session
            session['user'] = {
                'email': user['email'],
                'username': user['username']  
            }

            # Redirect based on the selected option
            tenant_page_choice = request.form.get('tenant_page_choice')
            if tenant_page_choice == 'energy':
                return redirect(url_for('energy'))
            elif tenant_page_choice == 'information':
                return redirect(url_for('tenant'))

            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))


def login_required(route_function):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            flash('Login required', 'danger')
            return redirect(url_for('login'))
        return route_function(*args, **kwargs)
    return wrapper


@app.teardown_appcontext
def close_mongo_client(exception=None):
    mongo_client = g.pop('mongo_client', None)
    if mongo_client is not None:
        mongo_client.close()

if __name__ == "__main__":
    app.run()
