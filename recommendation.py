from flask import Flask, request, jsonify
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Load dataset
df = pd.read_csv('./Data/combined_dta.csv', encoding='ISO-8859-1')

# Load or define the recommendation function (Item Based)
def recommend_items(product_name, num_recommendations=5):
    # Check if the product exists in the similarity matrix
    if product_name not in similarity_df.index:
        print(f"Product '{product_name}' not found in the dataset.")
        return []
    
    # Retrieve similarity scores for the specified product
    sim_scores = similarity_df[product_name]
    
    # Sort scores in descending order and exclude the product itself
    sim_scores = sim_scores.sort_values(ascending=False).drop(product_name)
    
    # Get the top recommendations
    top_items = sim_scores.head(num_recommendations).index
    top_scores = sim_scores.head(num_recommendations).values
    
    recommendations = list(zip(top_items, top_scores))
    return recommendations

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