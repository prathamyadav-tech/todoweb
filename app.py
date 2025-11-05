from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
from supabase import create_client, Client

app = Flask(__name__)

# Production config: read SECRET_KEY and Supabase credentials from environment
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Helper function to convert Supabase data to Todo object
class Todo:
    def __init__(self, id, title, desc, date_created):
        self.sno = id
        self.title = title
        self.desc = desc
        self.date_created = datetime.fromisoformat(date_created.replace('Z', '+00:00'))

    def __repr__(self):
        return f"{self.sno} - {self.title}"

# Create the todos table in Supabase if it doesn't exist
# Note: You'll need to create this table manually in your Supabase dashboard with the following SQL:
"""
create table todos (
    id bigint primary key generated always as identity,
    title varchar(200) not null,
    desc varchar(500) not null,
    date_created timestamp with time zone default timezone('utc', now())
);
"""



@app.route('/',methods=['GET','POST'])
def hello_world():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        if title and desc:
            data = supabase.table('todos').insert({
                "title": title,
                "desc": desc
            }).execute()
        return redirect(url_for('hello_world'))

    # Get all todos
    data = supabase.table('todos').select("*").order('date_created', desc=True).execute()
    todos = [Todo(item['id'], item['title'], item['desc'], item['date_created']) 
             for item in data.data]
    return render_template('index.html', alltodo=todos)

@app.route('/products')
def products():
    return 'this is product page'

@app.route('/delete/<int:sno>')
def delete(sno):
    supabase.table('todos').delete().eq('id', sno).execute()
    return redirect(url_for('hello_world'))

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        if title and desc:
            supabase.table('todos').update({
                "title": title,
                "desc": desc
            }).eq('id', sno).execute()
            return redirect(url_for('hello_world'))
    
    # Get the todo for editing
    data = supabase.table('todos').select("*").eq('id', sno).execute()
    if not data.data:
        return redirect(url_for('hello_world'))
    todo = Todo(data.data[0]['id'], data.data[0]['title'], 
                data.data[0]['desc'], data.data[0]['date_created'])
    return render_template('update.html', todo=todo)

if __name__=="__main__":
    app.run(debug=True, port=8000)
