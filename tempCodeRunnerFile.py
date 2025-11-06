
    try:
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

        alltodo = Todo.query.order_by(Todo.date_created.desc()).all()
        return render_template('index.html', alltodo=alltodo)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Database error: {str(e)}', 'error')
        return render_template('index.html', alltodo=[])

@app.route('/products')
def products():
    return 'this is product page'

@app.route('/delete/<int:sno>')
def delete(sno):
    try:
        todo = Todo.query.get_or_404(sno)
        db.session.delete(todo)
        db.session.commit()
        flash('Todo deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting todo: {str(e)}', 'error')
    return redirect(url_for('hello_world'))

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    try:
        todo = Todo.query.get_or_404(sno)
        if request.method == 'POST':
            title = request.form.get('title')
            desc = request.form.get('desc')
            if title and desc:
                todo.title = title
                todo.desc = desc
                db.session.commit()
    