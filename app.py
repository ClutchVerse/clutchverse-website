import os
import asyncio
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from mcstatus import JavaServer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clutchverse_secret_key_123'

# Render ke liye ekdum simple aur default path (Fix kiya hua)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Model User ke liye
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Minecraft Server Status Fetch karne ke liye
async def get_server_status():
    try:
        server = await JavaServer.async_lookup("learn.clutchverse.live")
        status = await server.async_status()
        return {"status": "Online", "players": status.players.online, "version": status.version.name}
    except Exception:
        return {"status": "Offline", "players": 0, "version": "N/A"}

# Home Page (Jahan sab kuch dikhega)
@app.route('/')
def home():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server_info = loop.run_until_complete(get_server_status())
    loop.close()
    
    videos = [{"title": "ClutchVerse Final Match Highlights", "url": "https://youtu.be/example1", "views": "1.2K"}]
    return render_template('index.html', server_info=server_info, videos=videos)

# Signup Route
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

# Login Route
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

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Support / Submit Ticket Route
@app.route('/support', methods=['POST'])
@login_required
def support():
    message = request.form.get('support_msg')
    print(f"[SUPPORT TICKET] Support Ticket from {current_user.username}: {message}")
    flash('Aapka Message mil gaya bhai, bhot jald check karenge!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Pehli baar run hone par database file automatic banegi
    app.run(debug=True)