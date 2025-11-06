from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = 'dev-secret'  # For local development only
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.debug = True

# SQLite Database Configuration
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'todo.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error="Internal server error"), 500

# Ensure database connection
def init_db():
    try:
        with app.app_context():
            db.create_all()
        print("Database initialized successfully!")
    except SQLAlchemyError as e:
        print(f"Error initializing database: {str(e)}")
        return False
    return True

# Todo model
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.title}"



@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        if title and desc:
            todo = Todo(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()
            flash('Todo added successfully!', 'success')
        else:
            flash('Title and description are required!', 'error')
        return redirect(url_for('hello_world'))

    todos = Todo.query.order_by(Todo.date_created.desc()).all()
    return render_template('index.html', alltodo=todos)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.get_or_404(sno)
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted successfully!', 'success')
    return redirect(url_for('hello_world'))

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.get_or_404(sno)
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        if title and desc:
            todo.title = title
            todo.desc = desc
            db.session.commit()
            flash('Todo updated successfully!', 'success')
            return redirect(url_for('hello_world'))
        flash('Title and description are required!', 'error')
    return render_template('update.html', todo=todo)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print(f"Database initialized at: {db_path}")
    app.run(debug=True, port=8000)
