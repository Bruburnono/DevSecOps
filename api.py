import flask
from flask import Flask, render_template, request, redirect, url_for, session
from flask import request, jsonify
from flask_mysqldb import MySQL

app = flask.Flask(__name__)
app.config["DEBUG"]=True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'base'
mysql = MySQL(app)

app.secret_key= b'\xe6\xe3\\\x0bp\xe6\x9f\xfcT\xfa\xa1\r<\xab\xf9\x1f\x87\xad\xb8\xf0\x17\x9f\x9c\xbd'
# Create some test data for our catalog in the form of a list of dictionaries.
books = [
    {'id': 0,
    'title': 'A Fire Upon the Deep',
    'author': 'Vernor Vinge',
    'first_sentence': 'The coldsleep itself was dreamless.',
    'year_published': '1992'},
    {'id': 1,
    'title': 'The Ones Who Walk Away From Omelas',
    'author': 'Ursula K. Le Guin',
    'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
    'year_published': '1973'},
    {'id': 2,
    'title': 'Dhalgren',
    'author': 'Samuel R. Delany',
    'first_sentence': 'to wound the autumnal city.',
    'year_published': '1975'}
]

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

# A route to return all of the available entries in ourcatalog. 
@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    return render_template("booksall.html", books=books)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            return redirect(url_for('dashboardprof'))
        else:
            return "Login Failed. Please check your username and password."
    return render_template('login.html')



@app.route('/dashboardprof', methods=['GET'])
def dashboardprof():
    if 'username' in session: 
        return render_template('sisiprof.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/dashboardeleve', methods=['GET'])
def dashboardeleve():
    if 'username' in session: 
        return render_template('sisieleve.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/teacher', methods=['GET', 'POST'])
def teach():
        if 'username' in session:
            if request.method == 'POST':  # Si c'est une requête POST
                print("Formulaire soumis")  # Ajoute cette ligne pour tester
                username = request.form['username']  # Récupère le nom d'utilisateur de la session
                course = request.form['course']  # Récupère le cours du formulaire
                note = request.form['grade']  # Récupère la note du formulaire
                
                cursor = mysql.connection.cursor()
                # Insère la note, le nom d'utilisateur et le cours dans la table 'grades'
                cursor.execute("INSERT INTO grades (username,cours,grade) VALUES (%s, %s, %s)", (username, course,note))
                mysql.connection.commit()  # Applique les modifications dans la base de données
                cursor.close()  # Ferme le curseur
                return redirect(url_for('teach'))  # Redirige vers la même page après soumission
        
            return render_template("teacher.html")  # Affiche le formulaire HTML
        return redirect(url_for('login'))  # Si l'utilisateur n'est pas connecté, redirige vers la page de connexion

@app.route('/grades', methods=['GET'])
def grades():
    if 'username' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM grades")
        all_grades = cursor.fetchall()  # Récupère toutes les lignes de la table grades
        cursor.close()

        return render_template("grades.html", grades=all_grades)  # Envoie les données à grades.html
    
    return redirect(url_for('login'))  # Si l'utilisateur n'est pas connecté, redirige vers la page de connexion


@app.route('/api/v1/resources/books', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        ID = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."
    # Create an empty list for our results
    results = []
    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for book in books:
        if book['id'] == ID:
            results.append(book)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return render_template("booksall.html", books=results)


app.run()


