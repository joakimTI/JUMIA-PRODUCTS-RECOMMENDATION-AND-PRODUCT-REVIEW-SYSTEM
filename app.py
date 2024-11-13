import streamlit as st
import pandas as pd
import pickle
import dill
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
# Load the pickled function

display_recommendations = dill.load(open("display_recommendations.pkl", "rb"))

# Load your data
df3 = dill.load(open("products_list.pkl", "rb"))

# Build a recommendation Function
def recommend_items(product_name, num_recommendations=5):
    # Combine the features
    df3['combined_features'] = (df3['product_name'].fillna('') + df3['brand'].fillna('') + df3['review_title'].fillna('') + df3['review'].fillna(''))
    # Initialize TF-IDF Vectorizer
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df3['combined_features'])

    # Set the number of latent features (e.g., 50)
    n_components = 50

    # Initialize and apply TruncatedSVD
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    item_features_matrix = svd.fit_transform(tfidf_matrix)
    
    # Calculate cosine similarity on the SVD-transformed matrix
    cosine_sim = cosine_similarity(item_features_matrix)
    # Convert to DataFrame for ease of use
    cosine_sim_df = pd.DataFrame(cosine_sim, index=df3['product_name'], columns=df3['product_name'])
    # Check if the product exists in the similarity DataFrame
    if product_name not in cosine_sim_df.columns:
        print(f"Product '{product_name}' not found in dataset.")
        return []
    
    # Get similarity scores for the product and sort by descending order
    sim_scores = cosine_sim_df[product_name].sort_values(ascending=False)
    
    # Exclude the product itself from recommendations
    sim_scores = sim_scores.drop(product_name)
    
    # Get the top recommendations based on similarity scores
    top_recommendations = sim_scores.head(num_recommendations).index.tolist()
    
    return top_recommendations

def display_recommendations(product_name, data, num_recommendations=5):
    # Get the list of recommended items
    recommendations = recommend_items(product_name, num_recommendations)
    
    # Display the original product for context
    st.write(f"### Recommendations for '{product_name}':\n")

    # Loop through the recommendations and display details from the dataset
    for rec in recommendations:
        # Filter the dataset to get details of the recommended item
        rec_data = data[data['product_name'] == rec]
        
        if not rec_data.empty:
            st.write(f"**Product Name:** {rec_data['product_name'].values[0]}")
            st.write(f"**Category:** {rec_data['Category'].values[0]}")
            st.write(f"**Ratings:** {rec_data['overall_ratings'].values[0]}")
            st.write(f"**Price:** ${rec_data['price'].values[0]:,.2f}")
            st.write("—" * 10)
        else:
            st.write(f"Details for '{rec}' not found in dataset.")

# Streamlit app logic
st.title("Product Recommendations")

# Get product name input from the user

product_name = st.selectbox("Select movie from dropdown", df3['product_name'])

if product_name:
    st.write(f"Recommendations for '{product_name}':")
    
    # Display recommendations using the loaded function
    display_recommendations(product_name, df3)
