from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import os
from flask_mysqldb import MySQL
from sqlalchemy.orm import sessionmaker
from register_form import RegisterForm
from project_form import ProjectForm
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'dt_admin'
app.config['MYSQL_PASSWORD'] = 'Mar1010n'
app.config['MYSQL_DB'] = 'studentsnewprojects_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#initialize MySQL
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')
    return "Hello John!  <a href='/logout'>Logout</a>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':

        #Get the fields
        POST_USERNAME = request.form['username']
        POST_PASSWORD = request.form['password']

        #Create a cursor
        cur = mysql.connection.cursor()
        #Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [POST_USERNAME])
        if result > 0:
            #Get the stored hash
            data = cur.fetchone()
            password = data['password']
            #Compare the passwords
        if sha256_crypt.verify(POST_PASSWORD, password):
            session['logged_in'] = True
            session['username'] = POST_USERNAME

            flash('You are now logged in', 'success')
            return redirect(url_for('dashboard'))

        else:
            error = 'Invalid Login'
            return render_template('login.html', error=error)
        #Close connection
        cur.close()
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create a cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email,username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        #commit to db
        mysql.connection.commit()
        cur.close()

        flash('You are now registered and can login', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    form = ProjectForm(request.form)

    if request.method == 'POST' and form.validate():
        tittle = form.tittle.data
        body = form.body.data

        # create a cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO projects(tittle, body, manager) VALUES(%s, %s, %s)", (tittle, body, session['username']))

        # commit to db
        mysql.connection.commit()
        cur.close()

        flash('Project successfully created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('create_project.html', form=form)

#Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route("/logout")
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
    return home()

@app.route('/dashboard')
@is_logged_in
def dashboard():
    #create cursor
    cur = mysql.connection.cursor()
    #Get Projects
    result = cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', projects=projects)
    else:
        msg = 'No Projects found'
        return render_template('dashboard.html', msg=msg)
    #Close the connection
    cur.close()

@app.route('/edit_project/<string:id>', methods=['GET', 'POST'])
def edit_project(id):
    cur = mysql.connection.cursor()
    # Get Project
    result = cur.execute("SELECT * FROM projects WHERE id = %s", [id])
    project = cur.fetchone()

    form = ProjectForm(request.form)
    # Populate article form fields
    form.tittle.data=project['tittle']
    form.body.data = project['body']

    if request.method == 'POST' and form.validate():
        tittle = form.tittle.data
        body = form.body.data

        # create a cursor
        cur = mysql.connection.cursor()
        cur.execute("UPDATE projects SET tittle = %s, body = %s WHERE id = %s", (tittle, body, id))
        # commit to db
        mysql.connection.commit()
        cur.close()

        flash('Project updated', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_project.html', form=form)



if __name__ == "__main__":
    app.secret_key='secret123'
    app.run(debug=False)
