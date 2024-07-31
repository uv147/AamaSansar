import os
import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
import numpy as np
import pandas as pd
# import seaborn as sns
import re
import string
# import matplotlib.pyplot as plt
# import surprise
from sklearn.metrics import precision_score
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import pairwise_distances
from scipy.stats import pearsonr
from scipy.sparse import csr_matrix

from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import sigmoid_kernel

from store.models import Product, Review, Category
from vendor.models import EcommerceUser


# generate dataset for recommendation
def data_collection(request):
    try:
        product = Product.objects.filter(status='Active')
        ecommerce_user = EcommerceUser.objects.filter(is_vendor=False, is_superuser=False)
        ecommerce_vendor = EcommerceUser.objects.filter(is_vendor=True, is_superuser=False)
        review = Review.objects.all()
        category = Category.objects.all()
        product_json = json.dumps(list(product.values()))
        ecommerce_user_json = json.dumps(list(ecommerce_user.values()), cls=DjangoJSONEncoder)
        ecommerce_vendor_json = json.dumps(list(ecommerce_vendor.values()), cls=DjangoJSONEncoder)
        review_json = json.dumps(list(review.values()), cls=DjangoJSONEncoder)
        category_json = json.dumps(list(category.values()), cls=DjangoJSONEncoder)
        with open(os.path.abspath("recommendation/dataset/product.json"), "w") as file:
            file.write(product_json[1:-1])
        with open(os.path.abspath("recommendation/dataset/user.json"), "w") as file:
            file.write(ecommerce_user_json[1:-1])
        with open(os.path.abspath("recommendation/dataset/vendor.json"), "w") as file:
            file.write(ecommerce_vendor_json[1:-1])
        with open(os.path.abspath("recommendation/dataset/review.json"), "w") as file:
            file.write(review_json[1:-1])
        with open(os.path.abspath("recommendation/dataset/category.json"), "w") as file:
            file.write(category_json[1:-1])

        return product, review
    except:
        pass
    return None


# def data_cleaning(request):
#     data_collection(request)
#     df1 = pd.read_json(os.path.abspath("recommendation/dataset/product.json"), lines=True)
#     df3 = pd.read_json(os.path.abspath("recommendation/dataset/review.json"), lines=True)
#     df1 = df1.drop(columns=['user_id', 'thumbnail', 'image'])
#     df3 = df3.drop(columns=['id', 'created_at']).rename(columns={'product_id': 'id', 'created_by_id': 'user_id'})
#     df = pd.merge(df1, df3, on="id", how="left").dropna()
#     df['reviews'] = df['content']
#     df = df.drop(['content'], axis=1)
#     relevant_columns = ['user_id', 'id', 'reviews', 'rating']
#     df = df[relevant_columns]
#     nltk.download('omw-1.4')
#     nltk.download('stopwords')
#     nltk.download('wordnet')
#
#     def preprocess_text(text):
#         # Remove non-alphanumeric characters and symbols
#         text = re.sub(r'[^A-Za-z0-9 ]+', '', text)
#         # Convert to lowercase
#         text = text.lower()
#         # Tokenization
#         tokens = text.split()
#         # Remove stop words
#         stop_words = set(stopwords.words('english'))
#         tokens = [token for token in tokens if token not in stop_words]
#         # Lemmatization
#         lemmatizer = WordNetLemmatizer()
#         tokens = [lemmatizer.lemmatize(token) for token in tokens]
#         # Join the tokens back into a single string
#         preprocessed_text = ' '.join(tokens)
#         return preprocessed_text
#
#     # Apply the text preprocessing function to the 'reviewText' column
#     df['preprocessed_review'] = df['reviews'].apply(preprocess_text)
#
#     def recommend_popularity_based(df, k=10):
#         # Group the data by 'asin' and count the occurrences
#         popularity = df.groupby('id').size().reset_index(name='popularity')
#
#         # Sort the items by popularity in descending order
#         popularity = popularity.sort_values('popularity', ascending=False)
#
#         # Get the top-k most popular items
#         top_items = popularity.head(k)['id']
#
#         return top_items.tolist()
#
#     # Example usage
#     top_items = recommend_popularity_based(df, k=10)
#     print("Top Recommended Items:")
#     for i in top_items:
#         print(f"Product_id: {i}")
#
#     ratings_new = df
#     review_texts = ratings_new['preprocessed_review'].astype(str)
#     tfidf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), stop_words='english', lowercase=True, encoding='utf-8')
#     tfidf_matrix = tfidf.fit_transform(review_texts)
#     sim_scores = linear_kernel(tfidf_matrix, tfidf_matrix)
#
#     pvt = ratings_new.pivot_table(index='user_id', columns='id', values='rating')
#     pvt.fillna(0, inplace=True)
#
#     cosine_sim = 1 - pairwise_distances(pvt, metric="cosine")
#     pearson_sim = 1 - pairwise_distances(pvt, metric="correlation")
#
#     def sim10_users(user_id, pvt, metric="correlation", k=10):
#         indices_sim = []
#         knn = NearestNeighbors(metric=metric, algorithm='brute')
#         knn.fit(pvt)
#         distances, indices_sim = knn.kneighbors(pvt.iloc[user_id, :].values.reshape(1, -1), n_neighbors=k + 1)
#         sims = 1 - distances.flatten()
#         return sims, indices_sim
#
#     def predict_rating(user_id, id, pvt, metric='pearson', k=10):
#         # user_id = float(user_id)
#         # id = int(id)
#         if user_id not in pvt.index:
#             print(f"User id {user_id} not found in the dataset.")
#             return None
#         if id not in pvt.columns:
#             print(f"Product id {id} not found in the dataset.")
#             return None
#
#         indices_usr = pvt.index.tolist()
#         indices_mov = pvt.columns.tolist()
#         indexu = indices_usr.index(user_id)
#         indexm = indices_mov.index(id)
#         pearson_sim = np.zeros(pvt.shape[0])
#         for i in range(pvt.shape[0]):
#             pearson_sim[i], _ = pearsonr(pvt.iloc[indexu], pvt.iloc[i])
#         sims = pearson_sim
#         mean_rating = pvt.iloc[indexu, :].mean()
#         rtSum = np.sum(sims) - 1
#
#         weighted_sum = 0
#         for i in range(len(indices_usr)):
#             if i == indexu:
#                 continue
#             else:
#                 rating_diff = pvt.iloc[i, indexm] - mean_rating
#                 weighted_sum += (sims[i] * rating_diff)
#
#         predicted_rating = mean_rating + (weighted_sum / rtSum)
#         return predicted_rating
#
#     def rec_product(id, similarity=None):
#         if id not in ratings_new['id'].tolist():
#             print("No recommendations found for the given id.")
#             return
#         index = ratings_new[ratings_new['id'] == id].index[0]
#         if similarity is None:
#             similarity_matrix = cosine_similarity(tfidf_matrix[index], tfidf_matrix)
#         else:
#             similarity_matrix = similarity[index].reshape(1, -1)
#         if isinstance(similarity_matrix, np.ndarray):
#             rec10_ind = np.argsort(similarity_matrix, axis=1)[:, -11:-1][:, ::-1].flatten()
#         else:
#             rec10_ind = [0]
#         recommended = pd.DataFrame({
#             'id': ratings_new.iloc[rec10_ind]['id'].tolist(),
#             'preprocessed_review': ratings_new.iloc[rec10_ind]['preprocessed_review'].tolist(),
#         })
#         recommended = recommended[recommended['id'] != asin]
#         if recommended.empty:
#             print("No recommendations found for the given id.")
#         else:
#             # print(recommended)
#             return recommended
#
#     def hybrid_recommendation(user_id, id, pvt, similarity_scores, content_weight=0.5, k=10):
#         # Content-based recommendation
#         user_id = float(user_id)
#         content_recommendations = rec_product(id, similarity=similarity_scores)
#         print(content_recommendations)
#         if content_recommendations is None:
#             return []  # Return an empty list if there are no content recommendations
#
#         content_recommendations = content_recommendations[content_recommendations['id'] != id].reset_index(drop=True)
#
#         # Collaborative filtering prediction
#         predicted_ratings = []
#         recommended_ids = set()  # To track recommended ASINs
#
#         for id in content_recommendations['id']:
#             if id not in recommended_ids:
#                 predicted_rating = predict_rating(user_id, id, pvt)
#                 predicted_ratings.append(predicted_rating)
#                 recommended_asins.add(id)
#
#         weighted_scores = content_weight * np.ones(len(content_recommendations)) + (1 - content_weight) * np.array(
#             predicted_ratings)
#         content_recommendations['weighted_score'] = weighted_scores
#         hybrid_recommendations = content_recommendations.sort_values(by='weighted_score', ascending=False)
#         recommended_ids.discard(id)
#         hybrid_recommendations = hybrid_recommendations[~hybrid_recommendations['id'].isin(recommended_ids)]
#         recommended_ids = hybrid_recommendations['id'].tolist()[:k]
#         print("Inside function", recommended_ids)
#         return recommended_ids
#
#     print(df.head())
#     predict_rating('12', '55', pvt)
#     rec_product('26', similarity=None)
#     recommended_ids = hybrid_recommendation('11', '74', pvt, sim_scores, k=10)
#     print(recommended_ids)


# load dataset for recommendation process
def read_dataset(request):
    data_collection(request)
    df_product = pd.read_json(os.path.abspath("recommendation/dataset/product.json"), lines=True)
    df_vendor = pd.read_json(os.path.abspath("recommendation/dataset/vendor.json"), lines=True)
    df_category = pd.read_json(os.path.abspath("recommendation/dataset/category.json"), lines=True)
    df_user = pd.read_json(os.path.abspath("recommendation/dataset/user.json"), lines=True)
    df_review = pd.read_json(os.path.abspath("recommendation/dataset/review.json"), lines=True)
    return df_product, df_vendor, df_category, df_user, df_review


# Content based filtering
def content_based_filtering(request, product_id):
    try:
        df_product, df_vendor, df_category, df_user, df_review = read_dataset(request)
        df_vendor = df_vendor.drop(columns=['password', 'last_login', 'is_superuser', 'first_name',
                                            'last_name', 'email', 'is_staff', 'is_active',
                                            'date_joined', 'is_vendor']).rename(columns={'id': 'user_id'})
        df_category = df_category.drop(columns=['slug']).rename(columns={'id': 'category_id'})
        df_product = df_product.drop(columns=['thumbnail', 'image'])
        df = pd.merge(df_product, df_vendor, on="user_id", how="left").dropna()
        df = pd.merge(df, df_category, on="category_id", how="left").dropna()
        df['content'] = df['description'] + df['title_x'] + df['title_y'] + df['username']
        relevant_columns = ['id', 'content', 'title_x']
        df = df[relevant_columns]

        tfv = TfidfVectorizer(min_df=3, max_features=None,
                              strip_accents='unicode', analyzer='word', token_pattern=r'\w{1,}',
                              ngram_range=(1, 3),
                              stop_words='english')
        df['content'] = df['content'].fillna('')
        tfv_matrix = tfv.fit_transform(df['content'])
        sig = sigmoid_kernel(tfv_matrix, tfv_matrix)
        indices = pd.Series(df.index, index=df['id']).drop_duplicates()

        # def give_content_based_recommendation(product_id, sig=sig):
        product_id = indices[product_id]
        sig_scores = list(enumerate(sig[product_id]))
        sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
        # sig_scores = sig_scores[:10]
        content_score = [1 - i[1] for i in sig_scores]
        product_indices = [i[0] for i in sig_scores]
        pid = df['id'].iloc[product_indices].tolist()
        data_tuples = list(zip(pid, content_score))
        con_recm_df = pd.DataFrame(data_tuples, columns=['product_id', 'score'])
        return pid, con_recm_df
    except Exception as e:
        pid = None
        con_recm_df = None
        return pid, con_recm_df


# Collaborative Based Filtering based on rating
def collaborative_based_filtering(request, product_id):
    try:
        df_product, df_vendor, df_category, df_user, df_review = read_dataset(request)
        df_product = df_product.drop(
            columns=['user_id', 'thumbnail', 'image', 'slug', 'price', 'description', 'status', 'category_id', ])
        df_review = df_review.drop(columns=['id', 'created_at']).rename(
            columns={'product_id': 'id', 'created_by_id': 'user_id'})
        df = pd.merge(df_product, df_review, on="id", how="left").dropna()
        df['reviews'] = df['content']
        df = df.drop(['content'], axis=1)
        relevant_columns = ['user_id', 'id', 'title', 'reviews', 'rating']
        df = df[relevant_columns]
        count_rating = (
            df.groupby(by=['id'])['rating'].count().reset_index().rename(columns={'rating': 'rating_count'})[
                ['id', 'rating_count']]
        )
        df_new = pd.merge(df, count_rating, on="id", how="left").dropna()
        df_new = df_new.drop_duplicates(['user_id', 'id'])
        df_new_pvt = df_new.pivot(index='id', columns='user_id', values='rating').fillna(0)
        df_new_pvt_matrix = csr_matrix(df_new_pvt.values)
        model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
        model_knn.fit(df_new_pvt_matrix)
        try:
            distances, indices = model_knn.kneighbors(df_new_pvt.iloc[product_id, :].values.reshape(1, -1),
                                                      n_neighbors=10)
            distance_value = distances[0]
            pid_array = [i for i in indices]
            pid = pid_array[0].tolist()
            data_tuples = list(zip(pid, distance_value))
            coll_recm_df = pd.DataFrame(data_tuples, columns=['product_id', 'distance'])
            return pid, coll_recm_df
        except:
            pid = None
            coll_recm_df = None
            return pid, coll_recm_df
    except Exception as e:
        pid = None
        coll_recm_df = None
        return pid, coll_recm_df


# combine content and collaborative based filtering
def hybrid_recommendation(request, product_id):
    con_pid, con_pid_df = content_based_filtering(request, product_id)
    coll_pid, coll_pid_df = collaborative_based_filtering(request, product_id)
    hybrid_df = None
    if coll_pid:
        hybrid_df = pd.merge(con_pid_df, coll_pid_df, on="product_id", how="left").dropna()
        hybrid_df['mean_value'] = hybrid_df.mean(axis=1)
        hybrid_df = hybrid_df.sort_values(by=['mean_value'])
        hybrid_df = hybrid_df['product_id'].tolist()
    return con_pid, coll_pid, hybrid_df


# Find out top 3 popular products
def recommend_popularity_based(request):
    df = pd.read_json(os.path.abspath("recommendation/dataset/product.json"), lines=True)
    popularity = df.groupby('id').size().reset_index(name='popularity')
    popularity = popularity.sort_values('popularity', ascending=False)
    top_items = popularity.head(3)['id'].tolist()
    products = Product.objects.filter(id__in=top_items)
    return products
