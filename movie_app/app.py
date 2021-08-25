#import psycopg2
#import pandas as pd
from flask import Flask, render_template, redirect, request, url_for, jsonify
import movie_app.similarity as similarity
from flask import request
from flask import make_response
import os

# JULIA ADDED: FOR SQL
import sqlalchemy
from sqlalchemy import create_engine, func
# from config import db_user, db_password, db_host, db_name, db_port
import pandas as pd

# Create an instance of Flask
app = Flask(__name__)

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '')

# Remove tracking modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Movie = create_classes(db)

# movie = Movie(name=name, lat=lat, lon=lon)
# db.session.add(pet)
# db.session.commit()

# Build engine
# engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
# END OF ADDED: FOR SQL



# Route to index.html template
@app.route("/")
def index():
  name = request.cookies.get('search')
  # Return index template
  return render_template("index.html", title=name)

# Route to similarity.py and function for ML and filter
@app.route("/similarity_scores", methods=['POST', 'GET'])
def similarity_scores():
  # Get the title
  if request.method == 'POST':  
    title = request.form['nm']
    # Define the name of movie
    name_of_movie = similarity.similarity(title)

  # Define the response
  resp = make_response(render_template('index.html', title=title))
  resp.set_cookie('search', title)

  return resp

# Get cookies
@app.route('/getcookie')
def getcookie():
  name = request.cookies.get('search')
  return name

# Route to female focused
@app.route("/femalefocused")
def femalefocused():
  name = request.cookies.get('search')
  # Direct to femalefocused.html
  return render_template("femalefocused.html", title=name)

# Route to international
@app.route("/international")
def international():
  name = request.cookies.get('search')
  # Direct to international.html
  return render_template("international.html", title=name)

# Route to low budget
@app.route("/lowbudget")
def lowbudget():
  name = request.cookies.get('search')
  # Direct to lowbudget.html
  return render_template("low_budget.html", title=name)

# Route to low budget
@app.route("/explore")
def explore():
  # Direct to explore.html
  return render_template("explore.html")

# Route to main low-budget explore
@app.route("/explore/low_budget")
def explore_lowbudget():
  # Direct to explore.html
  return render_template("em_low_budget.html")

# Route to popular low-budget explore
@app.route("/explore/low_budget/popular")
def explore_pop_lowbudget():
  # Direct to explore.html
  return render_template("em_pop_low.html")

# Route to unpopular low-budget explore
@app.route("/explore/low_budget/unpopular")
def explore_unpop_lowbudget():
  # Direct to explore.html
  return render_template("em_unpop_low.html")

# JULIA ADDED: FOR SQL
# Route to low budget api
@app.route("/api/low_budget")
def api_low_budget():
  # Read in low budget table
  results = pd.read_sql('SELECT * FROM low_budget', db)

  # Convert results to json
  results_json = results.to_json(orient='records') 

  return results_json
  
# Route to female api
@app.route("/api/female_led")
def api_female_led():
  # Read in low budget table
  results = pd.read_sql('SELECT * FROM female_led', db)

  # Convert results to json
  results_json = results.to_json(orient='records') 

  return results_json

# Route to international api
@app.route("/api/international")
def api_international():
  # Read in low budget table
  results = pd.read_sql('SELECT * FROM international', db)

  # Convert results to json
  results_json = results.to_json(orient='records') 

  return results_json

# Route to no filter api
@app.route("/api/no_filter")
def api_no_filter():
  # Read in low budget table
  results = pd.read_sql('SELECT * FROM no_filter', db)

  # Convert results to json
  results_json = results.to_json(orient='records') 

  return results_json
# END OF ADDED: FOR SQL

if __name__ == "__main__":
  app.run()