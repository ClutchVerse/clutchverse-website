import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from mcstatus import JavaServer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clutchverse_secret_key_123'

# Render ke liye ekdum sahi default path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ekdum simple aur direct function (Bina asyncio ke crash nahi hoga)
def get_server_status():
    try:
        server = JavaServer.lookup("learn.clutchverse.live")
        status = server.status()
        return {"status": "Online", "players": status.players.online, "version": status.version.name}
    except Exception:
        return {"status": "Offline", "players": 0, "version": "N/A"}

@app.route('/')
def home():
    # Direct status load hoga ab bina crash kiye
    server_info = get_server_status()
    videos = [{"title": "ClutchVerse Final Match Highlights", "url": "https://youtu.be/example1", "views": "1.2K"}]
    return render_template('index.html', server_info=server_info, videos=videos)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Bhai! Yeh username pehle se taken hai!', 'error')
            return redirect(url_for('signup'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account ban gaya bhai! Ab login karo.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Galti baat! Username ya Password galat hai.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/support', methods=['POST'])
@login_required
def support():
    message = request.form.get('support_msg')
    print(f"[SUPPORT TICKET] Support Ticket from {current_user.username}: {message}")
    flash('Aapka Message mil gaya bhai, bhot jald check karenge!', 'success')
    return redirect(url_for('home'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)