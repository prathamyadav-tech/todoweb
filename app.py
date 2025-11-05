from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os


app = Flask(__name__)

# Production config: read SECRET_KEY and DATABASE_URL from environment
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

# Use DATABASE_URL if provided (e.g., Postgres on Vercel), otherwise use a local SQLite file in instance/
basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Vercel and other providers often expose the DB URL as DATABASE_URL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Ensure instance folder exists and use sqlite there (local development)
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'todo.db')

db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200),nullable=False)
    desc = db.Column(db.String(500),nullable=False)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.title}"



@app.route('/',methods=['GET','POST'])
def hello_world():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        if title and desc:
            todo = Todo(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()
        return redirect(url_for('hello_world'))

    return render_template('index.html', alltodo=Todo.query.all())

@app.route('/products')
def products():
    return 'this is product page'


@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.get_or_404(sno)
    db.session.delete(todo)
    db.session.commit()
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
            return redirect(url_for('hello_world'))
    return render_template('update.html', todo=todo)

  
if __name__=="__main__":
    # Ensure database tables exist before starting the server
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=8000)
