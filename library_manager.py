import streamlit as st
import pandas as pd
import json
import os
import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Personal Library System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size:3rem !important;
        color: #4B0082;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    .sub-header {
        font-size: 2rem !important;
        color: #4B0082;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
        font-weight: 600;
    }
    .success-message {
        padding:1rem;
        background-color: #d4edda;
        border-radius: 0.37rem;
    }
    .warning-message {
        padding:1rem;
        background-color: #fff3cd;
        border-left: 5px solid #f59E0B;
        border-radius: 0.37rem;
    }
    .book-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3B82F6;
        transition: transform 0.3s ease;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .read-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: .875rem;
        font-weight: bold;
    }
    .unread-badge {
        background-color: #FF5722;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: .875rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Session state defaults
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load & Save functions
def load_library_data():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
                return True
    except Exception as e:
        st.error(f"Error loading library data: {e}")
    return False

def save_library_data():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library data: {e}")
        return False

# Book operations
def add_book(title, author, genre, read_status, publication_year):
    book = {
        "title": title,
        "author": author,
        "genre": genre,
        "read_status": read_status,
        "publication_year": publication_year,
        "added_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library_data()
    st.session_state.book_added = True
    time.sleep(0.5)

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library_data()
        st.session_state.book_removed = True
        return True
    return False

def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = [
        book for book in st.session_state.library
        if search_term in book[search_by].lower()
    ]
    st.session_state.search_results = results

def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    generas = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        generas[book["genre"]] = generas.get(book["genre"], 0) + 1
        authors[book["author"]] = authors.get(book["author"], 0) + 1
        decade = (book["publication_year"] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        "total_books": total_books,
        "read_books": read_books,
        "percent_read": percent_read,
        "generas": dict(sorted(generas.items(), key=lambda x: x[1], reverse=True)),
        "authors": dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        "decades": dict(sorted(decades.items()))
    }

def create_visulizations(stats):
    if stats['total_books'] == 0:
        return

    fig_read_status = go.Figure(data=[go.Pie(
        labels=["Read", "Unread"],
        values=[stats['read_books'], stats['total_books'] - stats['read_books']],
        hole=0.4,
        marker_colors=["#4CAF50", "#FF5722"],
    )])
    fig_read_status.update_layout(title_text='Read vs Unread Books', height=400)
    st.plotly_chart(fig_read_status, use_container_width=True)

    if stats['generas']:
        df = pd.DataFrame(list(stats['generas'].items()), columns=["Genre", "Count"])
        fig_genres = px.bar(df, x="Genre", y="Count", color="Count", color_continuous_scale="Plasma")
        fig_genres.update_layout(title_text="Books by Genre", height=400)
        st.plotly_chart(fig_genres, use_container_width=True)

    if stats['decades']:
        df = pd.DataFrame({
            'Decade': [f"{k}s" for k in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(df, x="Decade", y="Count", markers=True, line_shape="spline")
        fig_decades.update_layout(title_text="Books by Decade", height=400)
        st.plotly_chart(fig_decades, use_container_width=True)

# UI Navigation
load_library_data()
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_jzv1z0tz.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key='book_animation')

nav_options = st.sidebar.radio("Choose an option:", ["View Library", "Add Book", "Search Books", "Statistics"])

if nav_options == "Add Book":
    st.session_state.current_view = "add_book"
elif nav_options == "Search Books":
    st.session_state.current_view = "search_books"
elif nav_options == "Statistics":
    st.session_state.current_view = "statistics"
else:
    st.session_state.current_view = "library"

# Main Content
st.markdown("<h1 class='main-header'>Personal Library System</h1>", unsafe_allow_html=True)

if st.session_state.current_view == "add_book":
    st.markdown("<h2 class='sub-header'>Add a New Book 📖</h2>", unsafe_allow_html=True)
    with st.form(key="add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title")
            author = st.text_input("Author")
        with col2:
            genre = st.selectbox("Genre", [
                "Fiction", "Non-Fiction", "Science Fiction", "Fantasy", "Mystery", "Romance", "Horror", "Biography", "Self-Help", "History", "Others"
            ])
            read_status = st.radio("Read Status", options=["Read", "Unread"], horizontal=True)
        publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.datetime.now().year, step=1, value=2023)
        submit_button = st.form_submit_button(label="Add Book")
        if submit_button and title and author:
            add_book(title, author, genre, read_status == "Read", publication_year)

    if st.session_state.book_added:
        st.success("Book added successfully!")
        st.balloons()
        st.session_state.book_added = False

elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>Your Library 📚</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                    <div class='book-card'>
                        <h3>{book['title']}</h3>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Genre:</strong> {book['genre']}</p>
                        <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                        <p><span class='{"read-badge" if book['read_status'] else "unread-badge"}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
                    </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}"):
                        if remove_book(i):
                            st.rerun()
                with col2:
                    if st.button("Toggle Read", key=f"toggle_{i}"):
                        st.session_state.library[i]["read_status"] = not book["read_status"]
                        save_library_data()
                        st.rerun()

elif st.session_state.current_view == "search_books":
    st.markdown("<h2 class='sub-header'>Search Books 🔍</h2>", unsafe_allow_html=True)
    search_by = st.selectbox("Search by", options=["title", "author", "genre"])
    search_term = st.text_input("Enter search term:")
    if st.button("Search"):
        if search_term:
            search_books(search_term, search_by)
            if st.session_state.search_results:
                st.markdown(f"### Found {len(st.session_state.search_results)} result(s):")
                for book in st.session_state.search_results:
                    st.markdown(f"""
                        <div class='book-card'>
                            <h3>{book['title']}</h3>
                            <p><strong>Author:</strong> {book['author']}</p>
                            <p><strong>Genre:</strong> {book['genre']}</p>
                            <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                            <p><span class='{"read-badge" if book['read_status'] else "unread-badge"}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='warning-message'>No books found matching your search.</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "statistics":
    st.markdown("<h2 class='sub-header'>Library Statistics 📊</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books!</div>", unsafe_allow_html=True)
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats["total_books"])
        with col2:
            st.metric("Read Books", stats["read_books"])
        with col3:
            st.metric("Percent Read", f"{stats['percent_read']:.1f}%")
        if stats["authors"]:
            st.markdown("### Top Authors")
            for author, count in list(stats["authors"].items())[:5]:
                st.markdown(f"- {author}: {count} book{'s' if count > 1 else ''}")
        create_visulizations(stats)

# Footer
st.markdown("---")
st.markdown("© 2025 Sidra Haq Personal Library System", unsafe_allow_html=True)
