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
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'base'
mysql = MySQL(app)

app.secret_key= b'\xe6\xe3\\\x0bp\xe6\x9f\xfcT\xfa\xa1\r<\xab\xf9\x1f\x87\xad\xb8\xf0\x17\x9f\x9c\xbd'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','pdf'}

app.permanent_session_lifetime = timedelta(hours=1)  # Expiration après 1h d'inactivité

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    return render_template_string('''
        <h1>Forbidden</h1>
        <h1>Tu t'es cru chez toi ?</h1>
        <h1>Interdit aux plots/débutants</h1>
        <img src="{{ url_for('static', filename='images/never.webp') }}" alt="Forbidden Image">
    '''), 403

#@app.before_request
#def session_timeout():
    #""" Vérifie l'inactivité et détruit la session si le temps est écoulé """
    #if 'last_activity' in session:
        #last_activity = session['last_activity']
        #now = datetime.utcnow()
        #if now - last_activity > app.permanent_session_lifetime:
            #session.clear()  # Supprime toutes les données de session
            #return redirect(url_for('login'))  # Redirige vers la page de login
    #session['last_activity'] = datetime.utcnow()  # Met à jour le timestamp

@app.route('/', methods=['GET'])
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT title, content, author, date_posted, image_path FROM articles ORDER BY date_posted DESC")
    articles = cursor.fetchall()
    cursor.close()
    return render_template("home.html", articles = articles)

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
                    #if credentials[1] == "admin":
                        #return redirect(url_for('dashboard_admin'))
                    #if credentials[1] == "teacher":
                        #return redirect(url_for('dashboard_teacher'))
                    #if credentials[1] == "student":
                        #return redirect(url_for('dashboard_student'))
                else:
                    return "pas de clé", 401
            else:
                flash('Login failed: Invalid credentials', 'error')
        else:
            flash('Login failed: Invalid credentials', 'error')
    return render_template('login.html')


@app.route('/dashboard_teacher', methods=['GET'])
def dashboard_teacher():
    if 'secret_key' not in session:
        return abort(403)
    session_secret_key = session['secret_key']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data and user_data[1] in ['teacher', 'admin'] :
        return render_template('dashboard_teacher.html',user = user_data[2])
    else:
        abort(403)

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
        return render_template('dashboard_student.html', user = user_data[2])
    else:
        abort(403)
    return redirect(url_for('login'))

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
            print(username, role, user_id)
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



#@app.route('/dashboard_admin/add_user', methods=['POST'])
#def add_user():
    #new_username = request.form['username']
    #new_password = hash_password(request.form['password'])
    #new_role = request.form ['role']
    #cursor = mysql.connection.cursor()
    #cursor.execute("INSERT INTO users (username, password, role) VALUE (%s,%s,%s)", (new_username, new_password, new_role))
    #sisi = generate_secure_key()
    #cursor.execute("INSERT INTO honeypot (secret_key, role, username) VALUE (%s,%s,%s)", (sisi, new_role, new_username))
    #mysql.connection.commit()
    #return redirect('/dashboard_admin')

@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    if 'secret_key' not in session:
        return abort(403)
    session_secret_key = session['secret_key']
    print(session_secret_key)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
    user_data = cursor.fetchone()
    cursor.execute("SELECT student, subject, grade FROM grades WHERE teacher = %s", (user_data[2],))
    grades = cursor.fetchall()
    cursor.close()
    if user_data and user_data[1] in ['teacher', 'admin']:
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
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM honeypot WHERE role = 'student'")
        students = cursor.fetchall()
        student_list = [student[0] for student in students]
        cursor.close() 
        return render_template("teacher.html", students = student_list, grades = grades) 
    else:
        return abort(403)

@app.route('/grades', methods=['GET'])
def grades():
    if 'secret_key' not in session:
        return abort(403)
    session_secret_key = session['secret_key']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data and user_data[1] in ['student','admin'] :  
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT teacher, student, subject, grade FROM grades WHERE student = %s", (user_data[2],))
        grades = cursor.fetchall()
        if grades:
            notes = [float(grade[3]) for grade in grades]
            moyenne = sum(notes) / len(notes)
        else:
            moyenne = 0  # 
        return render_template("grades.html", grades=grades, moyenne=moyenne, student = user_data[2])
    else:
        abort(403)

@app.route('/mailbox', methods=['GET', 'POST'])
def mailbox():
    if 'secret_key' not in session:
        abort(403)
    user_id = session['secret_key']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username FROM honeypot WHERE secret_key = %s", (user_id,))
    blue = cursor.fetchone()
    if not blue :
        abort(403)
    if request.method == 'POST':
        receiver = request.form['receiver']
        subject = request.form['subject']
        content = request.form['message_content']
        if not receiver or not subject or not content:
            return "Erreur: Données manquantes", 400
        if receiver == "all":
            cursor.execute("SELECT username FROM users WHERE username != %s", (blue[0],))
            all_users = cursor.fetchall()           
            for user in all_users:
                cursor.execute(
                    "INSERT INTO mailbox (sender, receiver, content, subject, sent_at) VALUES (%s, %s, %s, %s, NOW())",
                    (blue[0], user[0], content, subject)
                )
        else:
            cursor.execute(
                "INSERT INTO mailbox (sender, receiver, content, subject, sent_at) VALUES (%s, %s, %s, %s, NOW())",
                (blue[0], receiver, content, subject)
            )
        mysql.connection.commit()
        return redirect(url_for('mailbox'))
    cursor.execute("SELECT sender, receiver, subject, content, sent_at FROM mailbox WHERE receiver = %s ORDER BY sent_at DESC", (blue[0],))
    messages = cursor.fetchall()
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('mailbox.html', messages=messages, users=users, username=blue[0])
    
@app.route('/devoirs', methods=['GET', 'POST'])
def devoirs():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session.get('secret_key'),))
    user = cursor.fetchone()    
    if not user:
        abort(403)
    if request.method == 'POST':
        # Récupérer l'énoncé et le fichier
        enon = request.form['enonce']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Enregistrer le fichier sur le serveur
            file_path = f'static/uploads/{filename}'.replace("\\", "/")
        
        
            # Insérer le chemin du fichier et l'énoncé dans la base de données
            cursor.execute("INSERT INTO devoirs (enonce, path) VALUES (%s, %s)", (enon, file_path))
            mysql.connection.commit()
         

     #Récupérer tous les devoirs (énoncé et chemin) après l'ajout
    cursor.execute("SELECT enonce, path FROM devoirs")
    devoirs = cursor.fetchall()  # Récupérer tous les devoirs
    cursor.close()
    return render_template("devoir.html", devoirs=devoirs)

  

@app.route('/devoirs_liste', methods=['GET'])
def devoirs_liste():
    if 'secret_key' not in session:
        abort(403)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT enonce, path FROM devoirs")
    devoirs = cursor.fetchall()  # Récupérer tous les devoirs (énoncé et chemin)
    cursor.close()
    return render_template('devoirs_liste.html', devoirs=devoirs)


@app.route('/agenda', methods=['GET'])
def agenda():
    if 'secret_key' not in session:
        return abort(403)
    session_secret_key = session['secret_key']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session_secret_key,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data : 
        return render_template('agenda.html')
    else:
        abort(403)

@app.route('/dashboard')
def dashboard():
    if 'secret_key' not in session:
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session.get('secret_key'),))
    user_data = cursor.fetchone()
    if user_data and session.get('role') == 'admin':
        return redirect(url_for('dashboard_admin'))
    if user_data and session.get('role') == 'teacher':
        return redirect(url_for('dashboard_teacher'))
    if user_data and session.get('role') == 'student':
        return redirect(url_for('dashboard_student'))
    else:
        return abort(403)

@app.route('/write_article', methods=['GET', 'POST'])
def write_article():
    if 'secret_key' not in session or session.get('role') not in ['admin', 'teacher']:
        return abort(403)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT secret_key, role, username FROM honeypot WHERE secret_key = %s", (session.get('secret_key'),))
        user_data = cursor.fetchone()
        if not user_data:
            return abort(403)
        date_posted = datetime.now()
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_path = f'static/uploads/{filename}' 
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO articles (title, content, author, date_posted, image_path) VALUES (%s, %s, %s, %s, %s)",
            (title, content, user_data[2], date_posted, image_path)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('home'))
    return render_template('write_article.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

app.run()
