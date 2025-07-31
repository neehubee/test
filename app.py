from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# Load and clean the dataset
df = pd.read_csv("cleaned.csv")
df = df[df["Clean_Genre"].notna()].reset_index(drop=True)

# Vectorize genres
tfidf = TfidfVectorizer(stop_words='english')
genre_vectors = tfidf.fit_transform(df['Clean_Genre'])

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    user_input_genre = data.get('genre', '').strip()

    if not user_input_genre:
        return jsonify({"error": "Genre input is empty."}), 400

    # Transform user input to vector
    input_vec = tfidf.transform([user_input_genre])
    similarity_scores = cosine_similarity(input_vec, genre_vectors).flatten()

    # Get top 20 matches by similarity
    top_indices = similarity_scores.argsort()[-20:][::-1]

    # Get matching books and filter by rating > 0
    recommended_books = df.iloc[top_indices].copy()
    recommended_books = recommended_books[recommended_books['average_rating'] > 0]

    # Sort again by rating (optional)
    recommended_books = recommended_books.sort_values(by='average_rating', ascending=False)

    # Limit to top 10
    top_books = recommended_books[['Title', 'Author', 'average_rating', 'Clean_Genre']].head(10)

    # Fallback if no good books found
    if top_books.empty:
        return jsonify({"message": "No high-rated books found for this genre."}), 200

    return jsonify(top_books.to_dict(orient='records'))

if __name__ == '__main__':
    import os
    port=int (os.environ.get('PORT',7860))
    app.run(host='0.0.0.0',port=port,debug=False)

