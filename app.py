import flask
from flask import Flask, render_template, request, redirect, url_for, session, abort, render_template_string, flash
from flask import request, jsonify
from flask_mysqldb import MySQL
import bcrypt
import secrets 
import string
from datetime import datetime
from werkzeug.utils import secure_filename
import os 
from datetime import timedelta, datetime

app = flask.Flask(__name__)
app.config["DEBUG"]=True

# Configuration pour la connexion MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'base'
mysql = MySQL(app)

# Configuration de la clé secrète pour la gestion de la session
app.secret_key = b'\xe6\xe3\\\x0bp\xe6\x9f\xfcT\xfa\xa1\r<\xab\xf9\x1f\x87\xad\xb8\xf0\x17\x9f\x9c\xbd'

# Configuration du dossier de téléchargement des fichiers
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','pdf'}

# Durée de vie de la session après une heure d'inactivité
app.permanent_session_lifetime = timedelta(hours=1)  # Expiration après 1h d'inactivité

# Fonction pour vérifier si le fichier a une extension valide
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fonction pour générer une clé secrète aléatoire
def generate_secure_key(length=50):
    characters = string.ascii_letters + string.digits + "_+-/"
    secure_key = ''.join(secrets.choice(characters) for _ in range(length))    
    return secure_key

# Fonction pour hasher un mot de passe
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Fonction pour vérifier si le mot de passe correspond à un hash stocké
def verify_password(stored_hash, entered_password):
    return bcrypt.checkpw(entered_password.encode(), stored_hash.encode())

# Gestion des erreurs 403 (accès interdit)
@app.errorhandler(403)
def forbidden_error(error):
    return render_template_string('''
        <h1>Forbidden</h1>
        <h1>Tu t'es cru chez toi ?</h1>
        <h1>Interdit aux plots/débutants</h1>
        <img src="{{ url_for('static', filename='images/never.webp') }}" alt="Forbidden Image">
    '''), 403

# Route principale (Page d'accueil)
@app.route('/', methods=['GET'])
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT title, content, author, date_posted, image_path FROM articles ORDER BY date_posted DESC")
    articles = cursor.fetchall()
    cursor.close()
    return render_template("home.html", articles=articles)

# Route pour la connexion des utilisateurs
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT password, username FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()     
        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
                cursor.execute("SELECT secret_key, role FROM honeypot WHERE username=%s", (user[1],))
                credentials = cursor.fetchone()
                if credentials:
                    session.clear()
                    session['secret_key'] = credentials[0]
                    session['role'] = credentials[1]
                    return redirect(url_for('dashboard'))
                else:
                    return "pas de clé", 401
            else:
                flash('Login failed: Invalid credentials', 'error')
        else:
            flash('Login failed: Invalid credentials', 'error')
    return render_template('login.html')

# Route pour le tableau de bord de l'enseignant
@app.route('/dashboard_teacher', methods=['GET'])
def dashboard_teacher():
    if 'secret_key' not in session:
        return abort(403)
    session_secret_key = session['secret_key']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data and user_data[1] in ['teacher', 'admin']:
        return render_template('dashboard_teacher.html', user=user_data[2])
    else:
        abort(403)

# Route pour le tableau de bord de l'étudiant
@app.route('/dashboard_student', methods=['GET'])
def dashboard_student():
    if 'secret_key' not in session:
        return abort(403)
    session_secret_key = session['secret_key']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data and user_data[1] in ['student', 'admin']:
        return render_template('dashboard_student.html', user=user_data[2])
    else:
        abort(403)
    return redirect(url_for('login'))

# Route pour le tableau de bord de l'administrateur
@app.route('/dashboard_admin', methods=['GET','POST'])
def dashboard_admin():
    if not session.get('secret_key'):
        return abort(403)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key FROM honeypot WHERE id = 1")
    user_data = cursor.fetchone()
    if not user_data or session.get('secret_key') != user_data[0] or session.get('role') != "admin": 
        cursor.close()
        return abort(403) 
    if request.method == 'POST':
        action = request.form.get("action")
        username = request.form.get("username")
        role = request.form.get("role")
        user_id = request.form.get("id")
        password = request.form.get("password")
        if password :
            password2 = hash_password(password)
        if action == "add" and username and role and password:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password2, role))
            cursor.execute("INSERT INTO honeypot (secret_key, role, username) VALUE (%s,%s,%s)", (generate_secure_key(), role, username))
        elif action == "modify" and username and (role == 'student' or role == 'teacher' or role == 'admin') and user_id:
            cursor.execute("UPDATE users SET username = %s, role = %s WHERE username = %s", (username, role, user_id))
            cursor.execute("UPDATE honeypot SET username = %s, role = %s WHERE username = %s", (username, role, user_id))
        elif action == "delete" and user_id:
            cursor.execute("DELETE FROM users WHERE username = %s", (user_id,))
            cursor.execute("DELETE FROM honeypot WHERE username = %s", (user_id,))
            cursor.execute("DELETE FROM grades WHERE student = %s OR teacher = %s", (user_id, user_id))
        
        mysql.connection.commit()
    cursor.execute("SELECT username, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('admin.html', user_data=user_data, users=users)

# Route pour l'enseignant qui permet de gérer les notes des élèves
@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    if 'secret_key' not in session:
        return abort(403)
    session_secret_key = session['secret_key']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
    user_data = cursor.fetchone()
    cursor.execute("SELECT student, subject, grade FROM grades WHERE teacher = %s", (user_data[2],))
    grades = cursor.fetchall()
    cursor.close()
    if user_data and user_data[1] in ['teacher', 'admin']:
        if request.method == 'POST':
            student = request.form['student']
            subject = request.form['course'] 
            note = request.form['grade']
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO grades (teacher,student,subject,grade) VALUES (%s, %s, %s, %s)", (user_data[2], student, subject, note))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('teacher'))
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM honeypot WHERE role = 'student'")
        students = cursor.fetchall()
        student_list = [student[0] for student in students]
        cursor.close() 
        return render_template("teacher.html", students=student_list, grades=grades)
    else:
        return abort(403)

# Route pour l'affichage des notes d'un étudiant
@app.route('/grades', methods=['GET'])
def grades():
    if 'secret_key' not in session:
        return abort(403)
    session_secret_key = session['secret_key']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data and user_data[1] in ['student','admin']:  
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT teacher, student, subject, grade FROM grades WHERE student = %s", (user_data[2],))
        grades = cursor.fetchall()
        if grades:
            notes = [float(grade[3]) for grade in grades]
            moyenne = sum(notes) / len(notes)
        else:
            moyenne = 0  
        return render_template("grades.html", grades=grades, moyenne=moyenne, student=user_data[2])
    else:
        abort(403)
