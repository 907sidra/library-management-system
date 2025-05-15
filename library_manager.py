import streamlit as st
import pandas as pd
import json
import os
#import datatime 
import datetime
import time
import random
import plotly.express as px
#import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

#set page configuration
st.set_page_config(
    page_title="persnol library system",
    page_icon="📚" ,
    layout="wide",
    initial_sidebar_state="expanded",
)

#custom cs for styling
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
            border-radius: 5px solid #f59E0B;
    }
     .book-card {
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom:1rem;
            border-left:5px solid #3B82F6;
            transition: transform 0.3s ease;
    }
     .book-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
     .read-badge {
            background-color: #d1e7dd;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: .875rem;
            font-weight: bold;
    }
            .unread-badge {
            background-color: #f8d7da;
            color: white;
            padding: 0.25rem 0.75rem;
             border-radius: 1rem;
            font-size: .875rem;
            font-weight: bold;  
    
    }
     .action-button {
            margin-right: 0.5rem;
    }
     .stButton>button {
            b0rder-radius: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None
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

#load library data from json file
#"r" = read time
def load_library_data():
    try: 
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
                return True
    except Exception as e:
        st.error(f"Error loading library data: {e}")
    return False
 #save library data to json file
 #'w'= watch time
def save_library_data():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file)
            return True
    except Exception as e:
        st.error(f"Error saving library data: {e}")
        return False

#add book to library
def add_book(title, author, genre, read_status):
    book = {
        "title": title,
        "author": author,
        "genre": genre,
        "read_status": read_status,
        #strf is a method to define date and time format
        "added_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library_data()
    st.session_state.book_added = True
    time.sleep(0.5) # Add a delay of 0.5 seconds
   #remove books from library
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        st.session_state.library.pop(index)
        save_library_data()
        st.session_state.book_removed = True
        return True
    return False   

#search books in library
def search_books(search_term,search_by):
    search_term = search_term.lower()
    results = []

    for book in st.session_state.library:
        if search_by == "title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "genre" and search_term in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results

#calculate total books in library
def get_library_stats():
    total_books = len(st.session_state.library)# get lenght from st.session_state in library 
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0
    genera ={}
    authors = {}
    decades = {}

    for book in st.session_state.library:
             #count genera
         if book["genre"] in genera:
             genera[book["genre"]] += 1
         else:
             genera[book["genre"]] = 1
        #count author
         if book["author"] in authors:
            authors[book["author"]] += 1
         else:
            authors[book["author"]] = 1
        #count decades
         decades = (book["publication_year"] // 10) * 10   
         if decades in decades:
             decades[decades] += 1
         else:
                decades[decades] = 1

#sort by count
    generas = dict(sorted(generas.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))

    return {
         "total_books": total_books,
         "read_books": read_books,
         "percent_read": percent_read,
         "generas": generas,
         "authors": authors,
         "decades": decades
    }
def create_visulizations(states):
    # Create a pi chart for genres
    if states['total_books'] > 0:
       fig_read_status = go.Figure(data=[go.pie(
            labels=["Read", "Unread"],
            values=[states['read_books'], states['total_books'] - states['read_books']],
            hole=0.4,
            marker_colors=["#4CAF50", "#FF5722"],
    )])        
    fig_read_status.update_layout(
             title_text='Read vs Unread Books',
             showlegend=False,
             height=400
    )
    st.plotly_chart(fig_read_status, use_container_width=True)
    # Create a bar chart for genres
    if states['generas']:
        generas_df = pd.DataFrame({
            'Genre': list(states['generas'].keys()),
            'Count': list(states['generas'].values())
        })
        fig_genres = px.bar(
            generas_df,
            x="Genre",
            y="Count",
            color="Count", 
            color_continuous_scale= px.colors.sequential.Plasmas,
           )
        fig_genres.update_layout(
            title_text="Books by genres",
            xaxis_title="Genres",
            yaxis_title="Number of books",
            height=400
        )
        st.plotly_chart(fig_genres, use_container_width=True)
    if states['decades']:
        decades_df = pd.Dataframe({
            'Decade': [f"{decade}s" for decade in states['decades'].keys()],
            'Count': list(states['decades'].values())
        })
        fig_decades =px.line(
            decades_df,
            x="Decade",
            y="Count",
            markers=True,
            line_shape="spline",
        )
        fig_decades.update_layout(
            title_text="Books by decade",
            xaxis_title="Decade",
            yaxis_title="Number of books",
            height=400

        )
        st.plotly_chart(fig_decades,use_container_width=True)

#load library
load_library_data()
st.sidebar.markdown("<h1 style='text-align: center;'> Navigation</h1/>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assests9.lottiefiles.com/temp/1f20_aKAfIn.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key='book_animation')
nav_options = st.sidebar.radio(
    "choose an option:",
    ["View Library", "Add Book", "Search Books", "Statistics"])

if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add_book"
elif nav_options == "Search Books":
    st.session_state.current_view = "search_books"
elif nav_options == "Statistics":
    st.session_state.current_view = "statistics"

#main content
st.markdown("<h1 class='main-header'>Personal Library System</h1>", unsafe_allow_html=True)
if st.session_state.current_view == "add_book":
    st.markdown("<h2 class='sub-header'>Add a New Book📖</h2>", unsafe_allow_html=True)

    #adding books input form
    with st.form(key="add_book_form"):
        col1,col2 =st.columns(2)

        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author",max_chars=100)
        publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.datetime.now().year, step=1, value=2023)

        with col2:
            genre = st.text_input("Genre",[
                "Friction", "non-Friction", "Science Fiction", "Fantasy", "Mystery", "Romance", "Horror", "Biography", "Self-Help", "History" , "Others"
            ])
            read_status = st.radio("Read Status", options=["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"  
        #submit button
        submit_button = st.form_submit_button(label="Add Book")

        if submit_button and title and author:
            add_book(title, author, genre, read_bool, publication_year)
            
    if st.session_state.book_added:
        st.success("<div class='sucess-message'>Book added successfully!</div>",unsafe_allow_htmal=True)
        st.balloons()
        st.session_state.book_added = False
elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>Your Library 📚</h2>", unsafe_allow_html=True)

    #display library books
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i , book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""<div class='book-card'>
                            <h3>{book['title']}</h3>
                            <p><strong>Author:</strong> {book['author']}</p>
                            <p><strong>Genre:</strong> {book['genre']}</p>
                            <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                            <p><span class ='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
                            </div>""", unsafe_allow_html=True)
                
                col1,col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}", use_container_width=True):
                        if remove_book(i):
                           st.rerun()
                with col2:
                    new_status = not book['read_status']
                    status_label = "Mark as Read" if not book['read_status'] else "Mark as unread"
                    if st.button(status_label, key=f"status_{i}", use_container_width=True):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library_data()
                        st.rerun()
    if st.session_state.book_removed:
        st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)
        st.session_state.book_removed = False
elif st.session_state.cuurent_view == "search_books":   
    st.markdown("<h2 class='sub-header'>Search Books 🔍</h2>", unsafe_allow_html=True)
    #search books input form
    search_by = st.selectbox("Search by", options=["title", "author", "genre"])
    search_term = st.text_input("Enter search term:")

    if st.button("Search", use_container_width=False):
        if search_term:
            with st.spinner("Searching..."):
                time.sleep(10.5)
                search_books(search_term, search_by)
        if hasattr(st.session_state, "search_results"):
            if st.session_state.search_results:
                st.markdown(f"<h3> Found {len(st.session_state.search_results)} results:</h3>", unsafe_allow_html=True)
                for i, book in enumerate(st.session_state.search_results):
                    st.markdown(f"""<div class='book-card'>
                                <h3>{book['title']}</h3>
                                <p><strong>Author:</strong> {book['author']}</p>
                                <p><strong>Genre:</strong> {book['genre']}</p>
                                <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                                <p><span class ='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
                                </div>""", unsafe_allow_html=True)
        elif search_term:
            st.markdown("<div class='warning-message'>No books found matching your search.</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "statistics":
    st.markdown("<h2 class='sub-header'>Library Statistics 📊</h2>", unsafe_allow_html=True )
    if st.session_state.library:
        st.markdown('<div> class=warning message> Your library is empty. Add some books!</div>', unsafe_allow_html=True)
    else:
        stats = get_library_stats()
        cols1,cols2,cols3 = st.columns(3)
        with cols1:
            st.metric("Total Books", stats['total_books'])
        with cols2:
            st.metric("Read Books", stats['read_books'])
        with cols3:
            st.metric("Percent Read", f"{stats['percent_read']:.1f}%")
        if stats['authors']:
            st.markdown("<h3>Top Authors</h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats['authors'].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f"{author}:{count} book {'s' if count > 1 else ''}")
st.markdown("---")
st.markdown("copyright @ 2025 Sidra Haq Personal Library System", unsafe_allow_html=True)
            
