from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db?check_same_thread=False'
db = SQLAlchemy(app)
migrate = Migrate(app, db)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/')
def list():
    users = User.query.all()
    return render_template('list.html', users=users)

@app.route('/detail/<user_id>')
def detail(user_id):
    user = User.query.filter_by(id=user_id).first()
    return render_template('detail.html', user=user)

@app.route('/create', methods=['get', 'post'])
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
def delete(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('detail.html', user=user)
