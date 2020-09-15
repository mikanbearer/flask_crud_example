from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_login
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db?check_same_thread=False'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

admins = {'testadmin': {'password': '123'}}

class Admin(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(admin_name):
    if admin_name not in admins:
        return
    admin = Admin()
    admin.id = admin_name
    return admin

@login_manager.request_loader
def request_loader(request):
    admin_name = request.form.get('user')
    if admin_name not in admins:
        return
    admin = Admin()
    admin.id = admin_name
    admin.is_authenticated = request.form['password'] == admins[admin_name]['password']
    return admin

@app.login_manager.unauthorized_handler
def unauth():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin_name = request.form['user']
        try:
            if request.form['password'] == admins[admin_name]['password']:
                admin = Admin()
                admin.id = admin_name
                flask_login.login_user(admin)
                return redirect(url_for('list'))
        except:
            return render_template('login.html', error='Login Failed')
    return render_template('login.html')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/')
@flask_login.login_required
def list():
    users = User.query.all()
    return render_template('list.html', users=users)

@app.route('/detail/<user_id>')
@flask_login.login_required
def detail(user_id):
    user = User.query.filter_by(id=user_id).first()
    return render_template('detail.html', user=user)

@app.route('/create', methods=['get', 'post'])
@flask_login.login_required
def create():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('form.html')

@app.route('/update/<user_id>', methods=['get', 'post'])
@flask_login.login_required
def update(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('form.html', user=user)

@app.route('/delete/<user_id>', methods=['get', 'post'])
@flask_login.login_required
def delete(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('detail.html', user=user)
