import flask
from flask import Flask, render_template, request, redirect, url_for, session, abort, render_template_string
from flask import request, jsonify
from flask_mysqldb import MySQL
import bcrypt
import secrets 
import string

app = flask.Flask(__name__)
app.config["DEBUG"]=True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'base'
mysql = MySQL(app)

app.secret_key= b'\xe6\xe3\\\x0bp\xe6\x9f\xfcT\xfa\xa1\r<\xab\xf9\x1f\x87\xad\xb8\xf0\x17\x9f\x9c\xbd'

def generate_secure_key(length=50):
    characters = string.ascii_letters + string.digits + "_+-/"
    secure_key = ''.join(secrets.choice(characters) for _ in range(length))    
    return secure_key

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(stored_hash, entered_password):
    return bcrypt.checkpw(entered_password.encode(), stored_hash.encode())


@app.errorhandler(403)
def forbidden_error(error):
    return render_template_string('<h1>Forbidden</h1><h1>Bouge de la mgl</h1>'), 403

@app.route('/', methods=['GET'])
def home():
    return render_template("home.html")

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
                cursor.execute("SELECT * FROM honeypot WHERE id=%s", (str(user[0])))
                credentials = cursor.fetchone()
                if credentials:
                    session.clear()
                    session['secret_key'] = credentials[1]
                    session['role'] = credentials[2]
                    if credentials[2] == "admin":
                        return redirect(url_for('dashboard_admin'))
                    if credentials[2] == "teacher":
                        return redirect(url_for('dashboard_teacher'))
                    if credentials[2] == "student":
                        return redirect(url_for('dashboard_student'))
                else:
                    return "pas de clé", 401
            else:
                return "Mot de passe incorrect", 401
        else:
            return "Utilisateur non trouvé", 404
    return render_template('login.html')


@app.route('/dashboard_teacher', methods=['GET'])
def dashboard_teacher():
    if 'secret_key' and 'role' in session: 
        session_secret_key = session['secret_key']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
        user_data = cursor.fetchone()
        cursor.close()
        if user_data and session.get('role') == 'teacher' : 
            return render_template('dashboard_teacher2.html',user = user_data[2])
        else:
            abort(403)
    else:
        abort(403)
    return redirect(url_for('login'))

@app.route('/dashboard_student', methods=['GET'])
def dashboard_student():
    if 'secret_key' and 'role' in session: 
            session_secret_key = session['secret_key']
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
            user_data = cursor.fetchone()
            cursor.close()
            if user_data and session.get('role') == 'student' : 
                return render_template('dashboard_student.html', user = user_data[2])
    return redirect(url_for('login'))

@app.route('/dashboard_admin', methods=['GET'])
def dashboard_admin():
    if 'secret_key' in session:
        session_secret_key = session['secret_key']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT secret_key FROM honeypot WHERE id = 1")
        user_data = cursor.fetchone()
        cursor.close()
        if user_data and session.get('role') == 'admin':  
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT username, role FROM users")
            users = cursor.fetchall()
            cursor.close()
            return render_template('admin.html', user_data=user_data, users=users)
        else:
            return abort(403)
    return abort(403)


@app.route('/dashboard_admin/add_user', methods=['POST'])
def add_user():
    new_username = request.form['username']
    new_password = hash_password(request.form['password'])
    new_role = request.form ['role']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUE (%s,%s,%s)", (new_username, new_password, new_role))
    sisi = generate_secure_key()
    cursor.execute("INSERT INTO honeypot (secret_key, role, username) VALUE (%s,%s,%s)", (sisi, new_role, new_username))
    mysql.connection.commit()
    return redirect('/dashboard_admin')

@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
        if 'secret_key' and 'role' in session: 
            session_secret_key = session['secret_key']
            print(session_secret_key)
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
            user_data = cursor.fetchone()
            cursor.close()
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT username FROM honeypot WHERE role = 'student'")
            students = cursor.fetchall()
            student_list = [student[0] for student in students]
            cursor.close()
            if user_data and session.get('role') == 'teacher' : 
                if request.method == 'POST': 
                    print("Formulaire soumis")
                    student = request.form['student']
                    subject = request.form['course'] 
                    note = request.form['grade']                 
                    cursor = mysql.connection.cursor()                
                    cursor.execute("INSERT INTO grades (teacher,student,subject,grade) VALUES (%s, %s, %s, %s)", (user_data[2], student, subject, note))
                    mysql.connection.commit()  
                    cursor.close()
                    return redirect(url_for('teacher'))        
                return render_template("teacher.html", students = student_list) 
        else:
            return abort(403)

@app.route('/grades', methods=['GET'])
def grades():
    if 'secret_key' and 'role' in session: 
        session_secret_key = session['secret_key']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
        user_data = cursor.fetchone()
        cursor.close()
        if user_data and session.get('role') == 'student' : 
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT teacher, student, subject, grade FROM grades WHERE student = %s", (user_data[2],))
            grades = cursor.fetchall()
            return render_template("grades.html", grades=grades, student = user_data[2])
        else:
            abort(403)
    else:
        abort(403)
    return redirect(url_for('login'))  

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

app.run()
