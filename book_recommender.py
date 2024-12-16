# Importing Libraries

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns

# Importing Data

books = pd.read_csv('BX-Books.csv', sep=';', encoding='ISO-8859-1', on_bad_lines='skip')
users = pd.read_csv('BX-Users.csv', sep=';', encoding='ISO-8859-1', on_bad_lines='skip')
ratings = pd.read_csv('BX-Book-Ratings.csv', sep=';', encoding='ISO-8859-1', on_bad_lines='skip')


# Data Cleaning

print(books.shape)
print(users.shape)
print(ratings.shape)

### Books

books.head()

books.rename(columns={'Book-Title': 'title', 
                      'Book-Author': 'author', 
                      'Year-Of-Publication': 'publish_year', 
                      'Publisher': 'publisher',
                      'Image-URL-L': 'image_url'}, 
                      inplace=True)

books.isnull().sum()

books.fillna({'author': '', 
              'publisher': '', 
              'image_url': ''}, 
              inplace=True)
books.isnull().sum()

books.duplicated().sum()

books.drop(columns=['Image-URL-S', 'Image-URL-M'], inplace=True)

### Users

users.head()

users.rename(columns={'User-ID': 'user_id', 
                      'Location': 'location', 
                      'Age': 'age'}, 
                      inplace=True)

users.isnull().sum()

users.duplicated().sum()

### Ratings

ratings.head()

ratings.rename(columns={'User-ID': 'user_id', 
                        'Book-Rating': 'rating'}, 
                        inplace=True)

ratings.isnull().sum()

ratings.duplicated().sum()

ratings.columns

ratings.head(10)

ratings.shape

# users rated less than 10
user_rating_counts = ratings['user_id'].value_counts()
user_rating_counts[user_rating_counts < 10].shape

# keep users with 10 or more ratings
users_with_10_or_more = user_rating_counts[user_rating_counts >= 10].index
ratings = ratings[ratings['user_id'].isin(users_with_10_or_more)]
ratings.shape

### Merged Data

df = pd.merge(ratings, books, on='ISBN', how='inner')
df.shape

df.head(2)

df.title.nunique()

# books with less than 10 ratings
book_rating_counts = df['ISBN'].value_counts()
book_rating_counts[book_rating_counts < 10].shape

# remove books with less than 10 books
books_with_10_or_more = book_rating_counts[book_rating_counts >= 10].index
df = df[df['ISBN'].isin(books_with_10_or_more)]
df.shape

df.head()

df.reset_index(drop=True, inplace=True)
df.head()

# EDA

print('Num of Users: ', df['user_id'].nunique())
print('Num of Books: ', df['title'].nunique())

df['rating'].describe()

df['publisher'].value_counts()

df['author'].value_counts()

df['publish_year'].value_counts().sort_index()

df[df['publish_year']!=0]['publish_year'].plot(kind='hist', bins=20)
plt.xlim(1920, 2005)
plt.show()

# Data Preprocessing

### df

df.head()

book_mean_ratings = df.groupby('ISBN')['rating'].transform('mean')
df['book_rating'] = book_mean_ratings
df.head()

# the book has 2 versions, each has its own rating
df[df['title'] == 'Harry Potter and the Goblet of Fire (Book 4)'].head()

book_num_ratings = df.groupby('ISBN')['rating'].transform('count')
df['num_ratings'] = book_num_ratings
df.head()

# the book has 2 versions, each has its own rating
df[df['title'] == 'Artemis Fowl.']

df.to_csv('cleaned_df.csv')

### interaction matrix

interaction_matrix = df.pivot_table(index='user_id', columns='ISBN', values='rating', fill_value=0)
interaction_matrix.shape

interaction_matrix.isnull().sum().sum()

# normalize ratings
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
user_item_matrix_scaled = scaler.fit_transform(interaction_matrix)

from scipy.sparse import csr_matrix
sparse_matrix = csr_matrix(user_item_matrix_scaled)
sparse_matrix.shape

# Collaborative Filtering

### User-Based 

from sklearn.metrics.pairwise import cosine_similarity
user_similarity = cosine_similarity(sparse_matrix)
user_similarity_df = pd.DataFrame(user_similarity, index=interaction_matrix.index, columns=interaction_matrix.index)
user_similarity_df.shape

similar_users = user_similarity_df[8].sort_values(ascending=False)
similar_users

def get_recommendations(user_id, top_n=5):
    similar_users = user_similarity_df[user_id].sort_values(ascending=False).iloc[1:top_n+1].index
    
    recommended_books = interaction_matrix.loc[similar_users].mean(axis=0).sort_values(ascending=False).index
    user_rated_books = interaction_matrix.loc[user_id][interaction_matrix.loc[user_id] > 0].index
    recommended_books = [book for book in recommended_books if book not in user_rated_books]
    
    recommended_books = recommended_books[:top_n]
    book_titles = df[df['ISBN'].isin(recommended_books)][['ISBN', 'title', 'book_rating', 'num_ratings', 'author', 'publisher', 'image_url']].drop_duplicates(subset='ISBN')
    
    return book_titles

recommended_books = get_recommendations(user_id=8)
recommended_books

### Item-Based

item_similarity = cosine_similarity(sparse_matrix.T)
item_similarity_df = pd.DataFrame(item_similarity, index=interaction_matrix.columns, columns=interaction_matrix.columns)
item_similarity_df.shape

similar_books = item_similarity_df['034544003X'].sort_values(ascending=False)
similar_books

def get_item_recommendations(book_name, top_n=5):
    book_isbn = df[df['title'] == book_name]['ISBN'].values

    if len(book_isbn) == 0:
        return f"Book '{book_name}' not found in the dataset."

    book_isbn = book_isbn[0]

    if book_isbn not in item_similarity_df.index:
        return f"ISBN {book_isbn} not found in the similarity matrix."

    similar_items = item_similarity_df[book_isbn].sort_values(ascending=False)
    similar_items = similar_items.drop(book_isbn, errors="ignore")

    top_items = similar_items.head(top_n).index.tolist()
    recommended_books = df[df['ISBN'].isin(top_items)][['ISBN', 'title', 'book_rating', 'num_ratings', 'author', 'publisher', 'image_url']].drop_duplicates(subset='ISBN')
    return recommended_books

recommended_books = get_item_recommendations(book_name="Harry Potter and the Chamber of Secrets (Book 2)")
recommended_books



