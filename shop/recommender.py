from django.db.models import Q
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from .models import Product, Catagory


class ProductRecommender:
    def __init__(self):
        self.scaler = MinMaxScaler()

    def get_recommendations(self, product_id, num_recommendations=4):
        try:   
            products = Product.objects.filter(status=False)

            data = []
            for product in products:
                data.append({
                    'id': product.id,
                    'category': product.category.name,
                    # Ensure price is treated as float
                    'new_price': float(product.new_price),
                    'eco_score': product.eco_score
                })

            df = pd.DataFrame(data)

            # Normalize prices for better comparison
            categorical = pd.get_dummies(df[['category']])
            numerical = df[['new_price', 'eco_score']]

            scaled = self.scaler.fit_transform(numerical)
            scaled = pd.DataFrame(scaled, columns=numerical.columns)

            features = pd.concat([categorical, scaled], axis=1)
            similarity = cosine_similarity(features)

            current_idx = df[df['id'] == product_id].index[0]
            similar_scores = list(enumerate(similarity[current_idx]))
            similar_scores = sorted(
                similar_scores, key=lambda x: x[1], reverse=True)

            recommended_products = []
            current_product = Product.objects.get(id=product_id)
            price_range = current_product.new_price * 0.4  # 40% price range flexibility

            # Get recommendations within similar price range
            for idx, score in similar_scores[1:]:
                prod_id = df.iloc[idx]['id']
                product = Product.objects.get(id=prod_id)

                # Check if price is within reasonable range (in rupees)
                if abs(product.new_price - current_product.new_price) <= price_range:
                    recommended_products.append(product)
                    if len(recommended_products) >= num_recommendations:
                        break

            # If we don't have enough recommendations, add more without price constraint
            if len(recommended_products) < num_recommendations:
                for idx, score in similar_scores[1:]:
                    prod_id = df.iloc[idx]['id']
                    product = Product.objects.get(id=prod_id)
                    if product not in recommended_products:
                        recommended_products.append(product)
                        if len(recommended_products) >= num_recommendations:
                            break

            return recommended_products
        except:
            return Product.objects.filter(status=False)[:4]


"""from django.db.models import Q
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from .models import Product, Catagory

class ProductRecommender:
    def __init__(self):
        self.scaler = MinMaxScaler()
    
    def get_recommendations(self, product_id, num_recommendations=4):
        try:
            # Get all active products
            products = Product.objects.filter(status=False)
            
            # Convert to DataFrame
            data = []
            for product in products:
                data.append({
                    'id': product.id,
                    'category': product.category.name,
                    'new_price': product.new_price,
                    'eco_score': product.eco_score
                })
            
            df = pd.DataFrame(data)
            
            # Prepare features
            categorical = pd.get_dummies(df[['category']])
            numerical = df[['new_price', 'eco_score']]
            
            # Scale numerical features
            scaled = self.scaler.fit_transform(numerical)
            scaled = pd.DataFrame(scaled, columns=numerical.columns)
            
            # Combine features
            features = pd.concat([categorical, scaled], axis=1)
            
            # Calculate similarity
            similarity = cosine_similarity(features)
            
            # Get product index
            current_idx = df[df['id'] == product_id].index[0]
            
            # Get similar products
            similar_scores = list(enumerate(similarity[current_idx]))
            similar_scores = sorted(similar_scores, key=lambda x: x[1], reverse=True)
            
            # Get recommendations
            recommended_products = []
            for idx, score in similar_scores[1:num_recommendations+1]:
                prod_id = df.iloc[idx]['id']
                product = Product.objects.get(id=prod_id)
                recommended_products.append(product)
            
            return recommended_products
        except:
            return Product.objects.filter(status=False)[:4]"""
