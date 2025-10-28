import streamlit as st
import pandas as pd
import pickle
from surprise import SVD, Reader, Dataset

# --- मॉडल और डेटा लोड करें ---
@st.cache_resource
def load_data_and_model():
    """मॉडल, मूवी डेटा, और यूजर IDs को कैश (cache) में लोड करता है।"""
    try:
        # 1. प्रशिक्षित SVD मॉडल लोड करें
        with open('model/svd_model.pkl', 'rb') as f:
            algo = pickle.load(f)
        
        # 2. आवश्यक मूवी और रेटिंग डेटा लोड करें (मान लीजिए आपने पहले से ही training data का हिस्सा सेव किया है)
        # डिप्लॉयमेंट के लिए, आपको इन फ़ाइलों को भी GitHub पर डालना होगा
        movies_df = pd.read_csv('data/movies.csv') 
        ratings_df = pd.read_csv('data/ratings.csv')

        # केवल रेटिंग देने वाले यूनिक यूजर IDs की लिस्ट
        unique_users = sorted(ratings_df['userId'].unique())
        
        # मूवी ID से शीर्षक (title) मैप बनाने के लिए
        movie_titles = dict(zip(movies_df['movieId'], movies_df['title']))

        return algo, movies_df, movie_titles, unique_users

    except FileNotFoundError as e:
        st.error(f"ज़रूरी फ़ाइलें नहीं मिलीं: {e.filename}. डिप्लॉयमेंट से पहले 'model/svd_model.pkl' और 'data/' फ़ोल्डर में CSV फ़ाइलें सुनिश्चित करें।")
        st.stop()
    except Exception as e:
        st.error(f"डेटा लोड करने में त्रुटि: {e}")
        st.stop()

# मॉडल और डेटा लोड करें
algo, movies_df, movie_titles, unique_users = load_data_and_model()

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="मूवी रेटिंग प्रेडिक्टर")
st.title('⭐ मूवी रेटिंग प्रेडिक्शन (Collaborative Filtering)')
st.markdown("यह मॉडल **SVD (Singular Value Decomposition)** का उपयोग करके अनुमान लगाता है कि एक यूजर किसी चयनित मूवी को क्या रेटिंग देगा।")

st.markdown("---")

# 1. यूजर सिलेक्शन (Sidebar में)
st.sidebar.header("यूजर और मूवी चुनें")
selected_user_id = st.sidebar.selectbox(
    '1. यूजर ID चुनें:',
    unique_users,
    index=0
)

# 2. मूवी सिलेक्शन (Dropdown)
movie_list = sorted(movies_df['title'].tolist())
selected_movie_title = st.sidebar.selectbox(
    '2. मूवी का नाम चुनें:',
    movie_list,
    index=movie_list.index("Toy Story (1995)") if "Toy Story (1995)" in movie_list else 0
)

# 3. प्रेडिक्शन बटन
if st.sidebar.button('रेटिंग प्रेडिक्ट करें'):
    
    # मूवी ID प्राप्त करें
    try:
        selected_movie_id = movies_df[movies_df['title'] == selected_movie_title]['movieId'].iloc[0]
    except IndexError:
        st.error("चयनित मूवी ID डेटा में नहीं है।")
        st.stop()
        
    # SVD मॉडल से प्रेडिक्शन प्राप्त करें
    # uid: यूजर ID, iid: मूवी ID, r_ui: वास्तविक रेटिंग (None, क्योंकि हम प्रेडिक्ट कर रहे हैं)
    prediction = algo.predict(uid=selected_user_id, iid=selected_movie_id, r_ui=None)
    
    # अनुमानित रेटिंग (Predicted Rating)
    estimated_rating = round(prediction.est, 2)
    
    # --- आउटपुट दिखाएँ ---
    st.subheader("💡 रेटिंग का अनुमानित परिणाम:")
    
    # रेटिंग को रंगीन कार्ड में दिखाएँ
    col1, col2 = st.columns([1, 4])
    with col1:
        st.metric(label=f"यूजर ID: {selected_user_id} के लिए", value=f"{estimated_rating} / 5.0")
    
    with col2:
        st.info(f"यूजर **ID {selected_user_id}** के लिए, मूवी **'{selected_movie_title}'** की अनुमानित रेटिंग है: **{estimated_rating}** (5 में से)।")

st.markdown("---")
st.caption("यह एक मशीन लर्निंग आधारित प्रेडिक्शन है। यह मॉडल उस पैटर्न पर आधारित है जो अन्य समान यूजर्स ने विभिन्न मूवीज़ को रेट करते समय दिखाया है।")
