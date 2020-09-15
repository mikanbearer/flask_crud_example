from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_login
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_bootstrap import Bootstrap
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db?check_same_thread=False'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# flask_sqlalchemy
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return '<User %r>' % self.username

#flask_migrate
migrate = Migrate(app, db)


#flask_login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

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


@app.login_manager.unauthorized_handler
def unauth():
    return redirect(url_for('login'))



# flask_wtf
csrf = CSRFProtect(app)

class LoginForm(FlaskForm):
    user = StringField('user', validators=[DataRequired()], render_kw={'placeholder': 'Username'})
    password = PasswordField('password', validators=[DataRequired()], render_kw={"placeholder": 'Password'})

class ModelForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])


# flask_bootstrap
Bootstrap(app)




@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.user.data
        password = form.password.data
        try:
            if password == admins[user]['password']:
                admin = Admin()
                admin.id = user
                flask_login.login_user(admin)
                return redirect(url_for('list'))
            else:
                error = 'password is incorrect'
        except:
            error = 'user not found'
        finally:
            pass
        return render_template('login.html', form=form, error=error)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

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
    form = ModelForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('form.html', form=form)

@app.route('/update/<user_id>', methods=['get', 'post'])
@flask_login.login_required
def update(user_id):
    user = User.query.filter_by(id=user_id).first()
    form = ModelForm(obj=user)
    if request.method == 'POST':
        user.username = form.username.data
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('detail', user_id=user_id))
    return render_template('form.html', user=user, form=form)

@app.route('/delete/<user_id>', methods=['get', 'post'])
@flask_login.login_required
def delete(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('detail.html', user=user)
