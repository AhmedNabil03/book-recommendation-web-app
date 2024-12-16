# Streamlit App for Book Recommendations

# Importing Libraries
import streamlit as st
import pandas as pd
from book_recommender import get_recommendations, get_item_recommendations

# Load data
df = pd.read_csv("cleaned_df.csv")

# Preprocess data for dropdowns
user_ids = sorted(df['user_id'].unique(), reverse=False)
book_titles = sorted(df['title'].unique(), reverse=False)

# Function to truncate book titles
def format_title(title, max_length=20):
    if len(title) > max_length:
        return title[:max_length] + "..."
    else:
        return title

# Function to truncate publisher
def format_publisher(publisher, max_length=15):
    if len(publisher) > max_length:
        return publisher[:max_length] + '...'
    else:
        return publisher

# Function to truncate author
def format_author(author, max_length=15):
    if len(author) > max_length:
        return author[:max_length] + '...'
    else:
        return author

# Streamlit App Layout
st.title("Book Recommendation System")
st.sidebar.header("Choose Recommendation Method")

# User-Based Recommendation
st.sidebar.subheader("User-Based Recommendations")
selected_user = st.sidebar.selectbox("Select User ID:", user_ids)

if st.sidebar.button("Get Recommendations for User"):
    recommended_books = get_recommendations(user_id=selected_user, top_n=6)
    st.subheader(f"Recommendations for User {selected_user}")

    recommended_books_list = recommended_books.to_dict('records')
    num_cols = 3
    cols = st.columns(num_cols)

    for i, book in enumerate(recommended_books_list):
        with cols[i % num_cols]:
            formatted_title = format_title(book['title'])
            formatted_publisher = format_publisher(book['publisher'])
            formatted_author = format_author(book['author'])
            st.markdown(f"""
                <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.2); display: flex; flex-direction: column; align-items: center; background-color: #f9f9f9;">
                    <img src="{book['image_url']}" width="100%" style="border-radius: 8px; object-fit: contain; max-height: 200px;" />
                    <div style="margin-top: 10px; text-align: left;">
                        <h5 style="color: #333;">{formatted_title}</h5>
                        <p><strong>Author:</strong> {formatted_author}</p>
                        <p><strong>Publisher:</strong> {formatted_publisher}</p>
                        <p><strong>Rating:</strong> {round(book['book_rating'], 2)}</p>
                        <p><strong>Reviews:</strong> {book['num_ratings']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Item-Based Recommendation
st.sidebar.subheader("Item-Based Recommendations")
selected_book = st.sidebar.selectbox("Select Book Title:", book_titles)

if st.sidebar.button("Get Recommendations for Book"):
    recommended_books = get_item_recommendations(book_name=selected_book, top_n=6)
    st.subheader(f"Books Similar to '{selected_book}'")

    recommended_books_list = recommended_books.to_dict('records')
    num_cols = 3
    cols = st.columns(num_cols)

    for i, book in enumerate(recommended_books_list):
        with cols[i % num_cols]:
            formatted_title = format_title(book['title'])
            formatted_publisher = format_publisher(book['publisher'])
            formatted_author = format_author(book['author'])
            st.markdown(f"""
                <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.2); display: flex; flex-direction: column; align-items: center; background-color: #f9f9f9;">
                    <img src="{book['image_url']}" width="100%" style="border-radius: 8px; object-fit: contain; max-height: 200px;" />
                    <div style="margin-top: 10px; text-align: center;">
                        <h3 style="color: #333;">{formatted_title}</h3>
                        <p><strong>Author:</strong> {formatted_author}</p>
                        <p><strong>Publisher:</strong> {formatted_publisher}</p>
                        <p><strong>Rating:</strong> {round(book['book_rating'], 2)}</p>
                        <p><strong>Reviews:</strong> {book['num_ratings']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
