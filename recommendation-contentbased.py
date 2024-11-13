from flask import Flask, request, jsonify
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Load dataset
df = pd.read_csv('./Data/combined_dta.csv', encoding='ISO-8859-1')

# Load or define the recommendation function (Content-Based Filtering)
def recommend_items(product_name, num_recommendations=5):
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

@app.route('/recommend', methods=['GET'])
def recommend():
    # Get product name and number of recommendations from request arguments
    product_name = request.args.get('product_name')
    num_recommendations = int(request.args.get('num_recommendations', 5))
    
    # Call the recommendation function
    recommendations = recommend_items(product_name, num_recommendations)
    
    # Return recommendations as JSON
    return jsonify({
        'product_name': product_name,
        'recommendations': recommendations
    })
if __name__ == '__main__':
    app.run(debug=True)