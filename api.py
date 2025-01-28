import flask
from flask import Flask, render_template
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"]=True

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