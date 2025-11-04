from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
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
