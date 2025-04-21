import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify, render_template
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# ========== Step 1: Load and Preprocess Dataset ==========
print("Loading dataset...")

# Load your Netnflix dataset
movies = pd.read_csv('netflix_titles.csv')

# Drop duplicates and NaNs in title
movies.drop_duplicates(subset='title', inplace=True)
movies = movies[movies['title'].notnull()]

# Fill missing important features with blanks
for feature in ['listed_in', 'cast', 'director', 'description']:
    movies[feature] = movies[feature].fillna('')

# Create a new column: Combined Features
def combine_features(row):
    return f"{row['listed_in']} {row['director']} {row['cast']} {row['description']}"

movies['combined_features'] = movies.apply(combine_features, axis=1)

# ========== Step 2: Feature Extraction ==========
print("Vectorizing text...")

# Use TF-IDF Vectorizer
tfidf = TfidfVectorizer(stop_words='english', max_features=10000)  # Limit features to 10k for performance
tfidf_matrix = tfidf.fit_transform(movies['combined_features'])

# ========== Step 3: Similarity Calculation ==========
print("Calculating similarity matrix...")

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Map movie titles to indices
indices = pd.Series(movies.index, index=movies['title'].str.lower()).drop_duplicates()

print("System ready!")

# ========== Step 4: Flask Routes ==========

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    movie_name = data.get('movie_name', '').strip().lower()

    if not movie_name:
        return jsonify({"error": "Please provide a movie/show name."}), 400

    if movie_name not in indices:
        return jsonify({"error": f"Movie/Show '{movie_name}' not found in database!"}), 404

    idx = indices[movie_name]

    # Get pairwise similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort movies based on similarity
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Skip itself (first item) and pick top 5 recommendations
    sim_scores = sim_scores[1:6]

    recommended_movies = []
    for i, score in sim_scores:
        recommended_movies.append({
            "title": movies.iloc[i]['title'],
            "genres": movies.iloc[i]['listed_in'],
            "description": movies.iloc[i]['description'],
            "cast": movies.iloc[i]['cast'],  # <-- Added this line
            "release_year": int(movies.iloc[i]['release_year']) if not pd.isna(movies.iloc[i]['release_year']) else None
        })

    return jsonify({"recommendations": recommended_movies})

# ========== Step 5: Run the App ==========

if __name__ == '__main__':
    app.run(debug=True)
