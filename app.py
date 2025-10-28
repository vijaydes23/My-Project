import streamlit as st
import pickle
import pandas as pd
import requests

# --- फ़ंक्शन: TMDB API से पोस्टर फेच करना ---
def fetch_poster(movie_id):
    """TMDB API से मूवी पोस्टर का URL फेच करता है।"""
    # यहाँ अपनी TMDB API Key डालें
    TMDB_API_KEY = "YOUR_TMDB_API_KEY" # अपनी API key से बदलें
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # HTTP errors के लिए
        data = response.json()
        
        # poster_path उपलब्ध होने पर full URL बनाना
        if data.get('poster_path'):
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return None # अगर पोस्टर उपलब्ध नहीं है
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return None

# --- फ़ंक्शन: सिफारिश (Recommendation) जेनरेट करना ---
def recommend(movie):
    """एक मूवी के लिए सिफारिशें (recommendations) जेनरेट करता है।"""
    # 1. मूवी का इंडेक्स (index) प्राप्त करें
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return ["Movie not found in the list."], []
    
    # 2. समानता मैट्रिक्स (similarity matrix) से दूरी प्राप्त करें
    distances = similarity[movie_index]
    
    # 3. सबसे ज़्यादा समान (similar) 5 मूवीज़ के इंडेक्स प्राप्त करें (खुद को छोड़कर)
    # enumerate() से इंडेक्स-दूरी पेयर मिलते हैं, फिर sort करते हैं
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_movies_posters = []
    
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        
        recommended_movies.append(movies.iloc[i[0]].title)
        
        # 4. पोस्टर फेच करें (या pre-loaded data से लें)
        poster_url = fetch_poster(movie_id) # लाइव API कॉल
        recommended_movies_posters.append(poster_url)
        
    return recommended_movies, recommended_movies_posters

# --- Streamlit ऐप का शीर्षक और लेआउट ---
st.set_page_config(layout="wide")
st.title('🎬 मूवी रेटिंग और सिफारिश प्रेडिक्शन')

# --- मॉडल और डेटा लोड करें ---
# ध्यान दें: Pickle फ़ाइलें आपके GitHub repo में 'model/' फ़ोल्डर में होनी चाहिए।
try:
    # 'rb' मोड में pickle फ़ाइलें लोड करें
    movies_dict = pickle.load(open('model/movies_list.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    
    # यदि आप समानता मैट्रिक्स को भी लोड कर रहे हैं
    similarity = pickle.load(open('model/similarity_matrix.pkl', 'rb'))
except FileNotFoundError:
    st.error("मॉडल फ़ाइलें 'model/' फ़ोल्डर में नहीं मिलीं। कृपया सुनिश्चित करें कि 'movies_list.pkl' और 'similarity_matrix.pkl' मौजूद हैं।")
    st.stop()
except Exception as e:
    st.error(f"फ़ाइल लोड करने में त्रुटि: {e}")
    st.stop()


# --- UI: मूवी सिलेक्शन ---
selected_movie_name = st.selectbox(
    'अपनी पसंदीदा मूवी चुनें जिसके आधार पर सिफारिशें मिलेंगी:',
    movies['title'].values
)

# --- UI: सिफारिश बटन ---
if st.button('सिफारिशें दिखाओ'):
    names, posters = recommend(selected_movie_name)
    
    # --- सिफारिशें ग्रिड लेआउट में दिखाओ ---
    if names[0] != "Movie not found in the list.":
        st.subheader(f"क्योंकि आपने '{selected_movie_name}' पसंद की, ये 5 फिल्में आपके लिए हैं:")
        
        # 5 कॉलम का लेआउट
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.text(names[0])
            if posters[0]:
                st.image(posters[0])
            else:
                st.info("पोस्टर उपलब्ध नहीं")

        with col2:
            st.text(names[1])
            if posters[1]:
                st.image(posters[1])
            else:
                st.info("पोस्टर उपलब्ध नहीं")

        with col3:
            st.text(names[2])
            if posters[2]:
                st.image(posters[2])
            else:
                st.info("पोस्टर उपलब्ध नहीं")

        with col4:
            st.text(names[3])
            if posters[3]:
                st.image(posters[3])
            else:
                st.info("पोस्टर उपलब्ध नहीं")

        with col5:
            st.text(names[4])
            if posters[4]:
                st.image(posters[4])
            else:
                st.info("पोस्टर उपलब्ध नहीं")
    else:
        st.warning(f"माफ़ करना, '{selected_movie_name}' के लिए डेटाबेस में कोई सिफारिश नहीं मिल पाई।")

# --- फुटर ---
st.markdown("---")
st.caption("यह प्रोजेक्ट Content-Based Filtering का उपयोग करके मूवी सिफारिशें जेनरेट करता है।")
