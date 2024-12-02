from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    due_date = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='Pending')
    
    # Foreign key to associate tasks with users
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

# Login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route after login
@app.route('/')
@login_required
def home():
    return render_template('index.html')

# Sign up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Hashing the password using the default method (PBKDF2)
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username already exists!', 'danger')
            return redirect(url_for('signup'))

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check username and password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route to display and filter tasks
@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        new_task = Task(title=title, description=description, due_date=due_date, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks'))

    filter_status = request.args.get('status', 'all')
    if filter_status == 'all':
        tasks = Task.query.filter_by(user_id=current_user.id).all()
    else:
        tasks = Task.query.filter_by(user_id=current_user.id, status=filter_status).all()

    return render_template('tasks.html', tasks=tasks)

# Route to edit tasks
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You are not authorized to edit this task!', 'danger')
        return redirect(url_for('tasks'))

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.due_date = request.form['due_date']
        task.status = request.form['status']
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks'))

    return render_template('tasks.html', task=task)

# Ensure that the database tables are created inside the application context
if __name__ == '__main__':
    with app.app_context():  # Ensure that the app context is active
        db.create_all()      # Create the database tables
    app.run(debug=True)
# from flask import Flask, render_template, redirect, url_for, request, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user

# # Initialize the app
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Initialize the database and login manager
# db = SQLAlchemy(app)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# # User model
# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), unique=True, nullable=False)
#     password = db.Column(db.String(150), nullable=False)

# # Login manager
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# # Sign up route
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         # Hashing the password using the default method (PBKDF2)
#         hashed_password = generate_password_hash(password)

#         # Create new user
#         new_user = User(username=username, password=hashed_password)

#         try:
#             db.session.add(new_user)
#             db.session.commit()
#             flash('Account created successfully!', 'success')
#             return redirect(url_for('login'))
#         except:
#             flash('Username already exists!', 'danger')
#             return redirect(url_for('signup'))

#     return render_template('signup.html')

# Run the app
if __name__ == '__main__':
    with app.app_context():  # Ensure that the app context is active
        db.create_all()      # Create the database tables
    app.run(debug=True)