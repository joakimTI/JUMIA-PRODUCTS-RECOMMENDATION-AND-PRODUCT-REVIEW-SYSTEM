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

categories = df3['Category'].unique()


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

def display_recommendations(product_name, data, num_recommendations=5, items_per_page=3):
    # Get the list of recommended items
    recommendations = recommend_items(product_name, num_recommendations)
    
    # Initialize carousel page in session state
    if 'carousel_page' not in st.session_state:
        st.session_state['carousel_page'] = 0

    # Calculate the total number of pages
    total_pages = (len(recommendations) + items_per_page - 1) // items_per_page
    
    # Display title for recommendations
    st.write(f"### Recommendations for '{product_name}':\n")
    
    # Display items for the current page
    start_index = st.session_state['carousel_page'] * items_per_page
    end_index = start_index + items_per_page
    current_page_recommendations = recommendations[start_index:end_index]
    
    # Display items in a row using columns
    cols = st.columns(items_per_page)
    for idx, rec in enumerate(current_page_recommendations):
        rec_data = data[data['product_name'] == rec]
        
        if not rec_data.empty:
            # Display each item in its respective column
            with cols[idx]:
                st.image(rec_data['image'].values[0], width=150)
                st.write(f"**Name:** {rec_data['product_name'].values[0]}")
                st.write(f"**Category:** {rec_data['Category'].values[0]}")
                st.write(f"**Ratings:** {rec_data['overall_ratings'].values[0]}")
                st.write(f"**Price:** Ksh{rec_data['price'].values[0]:,.2f}")
                st.write("—" * 10)
        else:
            st.write(f"Details for '{rec}' not found in dataset.")
    
    # Carousel navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Previous", key="prev"):
            st.session_state['carousel_page'] = (st.session_state['carousel_page'] - 1) % total_pages
    with col3:
        if st.button("Next", key="next"):
            st.session_state['carousel_page'] = (st.session_state['carousel_page'] + 1) % total_pages


# Streamlit app logic
st.title("Product Recommendations")

# Select category from dropdown
category_name = st.selectbox("Select Category from dropdown", df3['Category'].unique())

# Filter products based on selected category
filtered_products = df3[df3['Category'] == category_name]['product_name']

# Select product from the filtered list
product_name = st.selectbox("Select product from dropdown", filtered_products)
if product_name:
    st.write(f"Recommendations for '{product_name}':")
    
    # Display recommendations using the loaded function
    display_recommendations(product_name, df3)
