# from app import lowbudget
import pandas as pd
import os
import psycopg2

#To set up similarity matrix
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# SQL ALCHEMY
from flask import Flask
app = Flask(__name__)

# from flask_sqlalchemy import SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '')

# # Remove tracking modifications
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# # DATABASE CONNECTION: ADDED BY JULIA
# # Import config
# from config import api_key, db_user, db_password, db_host, db_port, db_name
# from sqlalchemy import create_engine, inspect
# # configure the connection string
# rds_connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
# # connect to the database
# engine = create_engine(rds_connection_string)
# conn = engine.connect()
# # END OF ADDED BY JULIA

#Could perform train_test_split and metrics.accuracy_score test if needed.   
#from sklearn.model_selection import train_test_split
#from sklearn.svm import SVC 
#from sklearn import metrics
# similarity(name_of_movie)

def similarity(name_of_movie):
  #import csv
  df = pd.read_csv("movie_app/data_cleaning/export/movie_db.csv")

  # Robin: lowercase code 
  name_of_movie = name_of_movie.lower()
  df["title"] = df["title"].str.lower()

  #set up new dataframe
  features = df[['index','title','release_date','cast','total_top_5_female_led','total_female_actors','percentage_female_cast','international','original_language','languages','genres','budget','budget_bins','popularity','tagline','keywords','production_companies','production_company_origin_country', 'director', 'overview']]

  #create combined_features row for similarity matrix
  def combine_features(row):
    # return row['cast']+" "+row['keywords']+" "+row['genres']+" "+row['tagline']+" "+row['production_companies']+" "+row['production_company_origin_country']
    # return row['cast']+" "+row['keywords']+" "+row['genres']+" "+row['tagline']+" "+row['overview']+" "+row['director']
    # return row['keywords']+" "+row['genres']+" "+row['tagline']+" "+row['overview']
    return row['cast']+" "+row['keywords']+" "+row['genres']+" "+row['tagline']+" "+row['production_companies']+" "+row['overview']+" "+row['director']

  for feature in features:
    features = features.fillna('')
    features['combined_features'] = features.apply(combine_features, axis=1)

  # define stop words
  stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}

  #create new CountVectorizer matrix
  cv = CountVectorizer(stop_words=stop_words, analyzer='word', min_df= 10)
  count_matrix = cv.fit_transform(features['combined_features'])

  #obtain cosine similarity matrix from the count matrix
  cosine_sim = cosine_similarity(count_matrix)

  #get movie title from movie index and vice-versa
  def get_title_from_index(index):
    return features[features.index == index]["title"].values[0]
  def get_index_from_title(title):
    return features[features.title == title]["index"].values[0]

  #find similarity scores for given movie and then enmerate over it.
  movie_user_likes = name_of_movie #"Toy Story 3"
  movie_index = get_index_from_title(movie_user_likes)
  similar_movies = list(enumerate(cosine_sim[movie_index])) 
  similar_movies

  #Sort the list similar_movies accroding to similarity scores in descending order. Since the most similar movie to a given movie is itself, discard the first elements after sorting movies.
  sorted_similar_movies = sorted(similar_movies, key=lambda x:x[1], reverse=True)[1:]

  # Create similarity df
  similarity_df = pd.DataFrame(similar_movies, columns=["index", "similarity_score"])
  similarity_df.set_index("index", inplace=True)

  # Merge original dataframe with similarity dataframe
  #merged_df = pd.merge(similarity_df, df)
  #merged_df.sort_values(by="similarity_score", ascending=False, inplace=True)
  joined_df = df.join(similarity_df, how='outer')
  joined_df = joined_df.sort_values(by="similarity_score", ascending=False)
  joined_df.reset_index(inplace=True, drop=True)

  # If the first title is the title of the chosen film, filter out
  if joined_df["title"][0] == movie_user_likes:
      joined_df = joined_df.loc[1:, :]
  else:
      joined_df = joined_df.loc[0:, :]

  # try:
  #   os.remove("./static/data/nofilterdata.js")
  #   print("nofilterdata.js has been removed")
  #   os.remove("./static/data/femaledata.js")
  #   print("femaledata.js has been removed")
  #   os.remove("./static/data/intldata.js")
  #   print("intldata.js has been removed")
  #   os.remove("./static/data/lowbudgetdata.js")
  #   print("lowbudgetdata.js has been removed")
  # except:
  #   print("No data files to remove")

  # No filter 
  nofilter = joined_df.sort_values(by="similarity_score", ascending=False)
  # nofilter.fillna('', inplace=True)
  # topnofilter = nofilter.iloc[1:21:1].to_json(orient="records")
  topnofilter = nofilter.iloc[1:21:1]

  # Drop previous table
  db.engine.execute('DROP TABLE IF EXISTS no_filter')
  topnofilter.to_sql(name='no_filter', con=conn, if_exists='append', index=False)

  # f = open("./static/data/nofilterdata.js", "w")
  # f.write("var data = ")
  # f.write(topnofilter)
  # f.close()

  # Female-Led
  # Change "percentage_female_directed" to "percentage_female_led" (once updated csv is pushed)
  female_led = joined_df.sort_values(by=["percentage_female_directed", "similarity_score"], ascending=False)
  # female_led.fillna('', inplace=True)
  # top_fem = female_led[:20].to_json(orient="records")
  top_fem = female_led[:20]

  db.engine.execute('DROP TABLE IF EXISTS female_led')
  top_fem.to_sql(name='female_led', con=conn, if_exists='append', index=False)

  # f = open("./static/data/femaledata.js", "w")
  # f.write("var data = ")
  # f.write(top_fem)
  # f.close()

  # International
  international = joined_df.sort_values(by=["international", "similarity_score"], ascending=False)
  # international.fillna('', inplace=True)
  # top_intl = international[:20].to_json(orient="records")
  top_intl = international[:20]

  db.engine.execute('DROP TABLE IF EXISTS international')
  top_intl.to_sql(name='international', con=conn, if_exists='append', index=False)
  # f = open("./static/data/intldata.js", "w")
  # f.write("var data = ")
  # f.write(top_intl)
  # f.close()

  # Low-Budget
  low_budget = joined_df.loc[joined_df["budget_bins"] == "0 to 15m"].copy()
  low_budget = low_budget.sort_values(by=["similarity_score"], ascending=False)
  # low_budget.fillna('', inplace=True)
  # top_lowbudget = low_budget[:20].to_json(orient="records")
  top_lowbudget = low_budget[:20]
  # print(top_lowbudget)

  db.engine.execute('DROP TABLE IF EXISTS low_budget')
  top_lowbudget.to_sql(name='low_budget', con=conn, if_exists='append', index=False)

  # f = open("./static/data/lowbudgetdata.js", "w")
  # f.write("var data = ")
  # f.write(top_lowbudget)
  # f.close()

  # data = {"low_budget": top_lowbudget, "international": top_intl, "female_led": top_fem, "all": topnofilter}
  # return data
  conn.close()