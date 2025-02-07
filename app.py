import flask
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import request, jsonify
from flask_mysqldb import MySQL
from flask_wtf import CSRFProtect
import bcrypt

app = flask.Flask(__name__)
app.config["DEBUG"]=True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'base'
mysql = MySQL(app)

app.secret_key= b'\xe6\xe3\\\x0bp\xe6\x9f\xfcT\xfa\xa1\r<\xab\xf9\x1f\x87\xad\xb8\xf0\x17\x9f\x9c\xbd'
csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = True


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(stored_hash, entered_password):
    return bcrypt.checkpw(entered_password.encode(), stored_hash.encode())


@app.route('/', methods=['GET'])
def home():
    return render_template("login.html")



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                session['user_id'] = user[0]
                session['username'] = user[1]
                if user[3] == "admin":
                    return redirect(url_for('dashboard_admin'))
                if user[3] == "teacher":
                    return redirect(url_for('dashboard_teacher'))
                if user[3] == "student":
                    return redirect(url_for('dashboard_student'))
            else:
                flash('Invalid password', 'error')
        else:
            flash('User not found', 'error')
    return render_template('login.html')



@app.route('/dashboard_teacher', methods=['GET'])
def dashboard_teacher():
    if 'username' in session: 
        return render_template('dashboard_teacher.html')
    return redirect(url_for('login'))

@app.route('/dashboard_student', methods=['GET'])
def dashboard_student():
    if 'username' in session: 
        return render_template('dashboard_student.html')
    return redirect(url_for('login'))

@app.route('/dashboard_admin', methods=['GET'])
def dashboard_admin():
    if 'username' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username, role FROM users")
        users = cursor.fetchall()
        cursor.close
        return render_template('admin.html', users=users)
    return redirect(url_for('login'))

@app.route('/dashboard_admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' in session and 'username' in request.form:
        username = request.form['username']        
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        mysql.connection.commit()
        cursor.close()
    return redirect('/dashboard_admin')

@app.route('/dashboard_admin/add_user', methods=['POST'])
def add_user():
    new_username = request.form['username']
    new_password = hash_password(request.form['password'])
    new_role = request.form ['role']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUE (%s,%s,%s)", (new_username, new_password, new_role))
    mysql.connection.commit()
    return redirect('/dashboard_admin')

@app.route('/teacher', methods=['GET', 'POST'])
def teach():
        if 'username' in session:
            if request.method == 'POST': 
                print("Formulaire soumis")
                username = request.form['username']
                course = request.form['course'] 
                note = request.form['grade']                 
                cursor = mysql.connection.cursor()                
                cursor.execute("INSERT INTO grades (username,course,grade) VALUES (%s, %s, %s)", (username, course,note))
                mysql.connection.commit()  
                cursor.close()
                return redirect(url_for('teach')) 
        
            return render_template("teacher.html") 
        return redirect(url_for('login')) 

@app.route('/grades', methods=['GET'])
def grades():
    if 'username' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM grades")
        all_grades = cursor.fetchall()
        cursor.close()
        return render_template("grades.html", grades=all_grades)
    return redirect(url_for('login'))  

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/v1/resources/books', methods=['GET'])
def api_id():
    if 'id' in request.args:
        ID = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."
    results = []


app.run()
