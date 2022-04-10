# -*- coding: utf-8 -*-
"""NLP Sentiment Analysis of Hotel Review.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1par_89_P28ynqzzTIMIsk1yqyWejtJ3O

# Import Package/Library
"""

# Import package/library
import re
import string
from collections import defaultdict
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import nltk
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from wordcloud import WordCloud, STOPWORDS
import pickle

pd.set_option("display.max_colwidth", 1000)
nltk.download("punkt")

st.set_page_config(
    page_title="Sentiment Analysis of Hotel Review",
    page_icon=(Image.open("hotel.png")),
    layout="wide"
    )

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🏨 Sentiment Analysis of Hotel Review")

# Create Stopwords for Bahasa Indonesia
nltk.download("stopwords")
id_stop = set(stopwords.words("indonesian"))

# Turn data into dataframe
df = pd.read_csv("review_hotel.csv")

# Turn 0 and 1 into 'Negatif' and 'Positif' and add them into the new column
df['category_new'] = df['category'].replace(0,'Negatif', regex=True).replace(1,'Positif', regex=True)

# Preprocess data
punctuations = string.punctuation

# Remove punctuation and turn into space
def punct2wspace(text):
    return re.sub(r"[{}]+".format(punctuations), " ", text)

# Remove enter and turn into space
def normalize_enter(text):
    return re.sub(r"\n+", " ", text)

# Turn double spaces into single space
def normalize_wspace(text):
    return re.sub(r"\s+", " ", text)

# Lowercase the letter
def casefolding(text):
    return text.lower()

# Combine all preprocessing
def preprocess_text(text):
    text = punct2wspace(text)
    text = normalize_enter(text)
    text = normalize_wspace(text)
    text = casefolding(text)
    return text

# Apply preprocessing and join the preprocessed text into the dataframe
df["preprocessed_text"] = df["review_text"].map(preprocess_text)

# Split a sentence into single word
words = df['preprocessed_text']
allwords = []
for wordlist in words.values:
  if wordlist not in id_stop:
    wordlist = wordlist.split()
    allwords += wordlist

allwords = pd.DataFrame(allwords)

# Filter the words with Stopwords (Bahasa Indonesia)
allwords_stopword = []
for wordlist in allwords[0].values: 
  if wordlist not in id_stop:
    allwords_stopword.append(wordlist)

# Check the polarity of the review, then create 'polarity' column and add it into the dataframe
df['polarity'] = df['preprocessed_text'].apply(lambda x:TextBlob(x).sentiment.polarity)

# Row A
st.header("Seberapa banyak sih tamu hotel yang tidak puas?")
a1, a2 = st.columns(2)
label = ["Tidak puas","Puas"]
with a1:
  plt.figure(figsize=(15,10))
  sns.set_style('ticks')
  sns.countplot(data=df, x='category', palette='Pastel1')
  sns.despine()
  plt.xlabel('(Ket: 0 = Tidak puas, 1 = Puas)', fontsize=30)
  plt.ylabel('Jumlah tamu', fontsize=30)
  plt.xticks(fontsize=24)
  plt.yticks(fontsize=24)
  plt.suptitle(' ', fontsize=32)
  plt.savefig('bar_chart.png')
  st.image(Image.open("bar_chart.png"))
with a2:
  st.subheader(" ")
  def pie_chart(dataset,column,label):
    plt.figure(figsize=(15,10))
    plt.pie(dataset[column].value_counts(),
            colors=sns.color_palette('Pastel1'),
            textprops={"fontsize":40},
            autopct='%0.2f%%'
            )
    plt.legend(label, fontsize=24)
    plt.savefig('pie_chart.png')

  pie_chart(df,'category',label)
  st.image(Image.open("pie_chart.png"))

# Row B
st.header("Bagaimana sih tanggapan tamu hotel?")
b1, b2 = st.columns((4,4))
with b1:
  # Print 3 random reviews with the highest polarity 
  st.subheader("Top 3 Ulasan Terbaik 👍")
  for index,review in enumerate(df.iloc[df['polarity'].sort_values(ascending=False)[:3].index]['review_text']):
    st.write('Ulasan {}:\n'.format(index+1),review)

with b2:
  # Print 3 random reviews with the lowest polarity 
  st.subheader("Top 3 Ulasan Terburuk 👎")
  for index,review in enumerate(df.iloc[df['polarity'].sort_values(ascending=True)[:3].index]['review_text']):
    st.write('Ulasan {}:\n'.format(index+1),review)

# Count number of letters in a single sentence
df['letter_count'] = df['preprocessed_text'].astype(str).apply(len)

# Row C
st.header("Benarkah ulasan negatif lebih panjang?")
c1, c2 = st.columns(2)
with c1:
  # Create new dataframe contains mean of letter count
  letter_avg = df.groupby('category')['letter_count'].mean()
  letter_avg = pd.DataFrame(letter_avg).reset_index()

  # Plot average number of letters per rating distribution
  plt.figure(figsize=(15,10))
  sns.set_style('ticks')
  sns.barplot(x='category', y='letter_count', palette='Pastel1', data=df)
  sns.despine()
  plt.xlabel('(Ket: 0 = Tidak puas, 1 = Puas)', fontsize=30)
  plt.ylabel('Rataaan jumlah huruf', fontsize=30)
  plt.xticks(fontsize=24)
  plt.yticks(fontsize=24)
  plt.suptitle(' ', fontsize=32)
  plt.savefig('letter_count.png')
  st.image(Image.open('letter_count.png'))
with c2:
  # Count the difference in the average number of letters per rating
  letter = df.groupby('category')['letter_count'].mean()
  letter = pd.DataFrame(letter).reset_index()

  letter_0 = letter[letter['category']==0]
  letter_1 = letter[letter['category']==1]
      
  class_0 = letter_0['letter_count'] 
  class_1 = letter_1['letter_count']

  selisih = int(class_0) - int(class_1)

  st.write("Panjang ulasan negatif ternyata ...") 
  st.metric(label="Rataan huruf ulasan negatif",
            value=str(int(class_0)),
            delta=str(selisih),
            delta_color='inverse')
  st.write("... 15 huruf lebih panjang dari ulasan positif.")

# Row D
st.header("Kata apakah yang muncul terbanyak?")
d1, d2 = st.columns(2)
with d1:
  # Plot Top 25 Most Common Words
  mostcommon_small = FreqDist(allwords_stopword).most_common(25)
  x, y = zip(*mostcommon_small)

  plt.figure(figsize=(15,10))
  plt.margins(0.02)
  plt.bar(x, y, color='lightseagreen')
  sns.despine()
  plt.ylabel('Frekuensi kemunculan', fontsize=30)
  plt.yticks(fontsize=24)
  plt.xticks(rotation=50, fontsize=18)
  plt.suptitle('', fontsize=32)
  plt.savefig('most_common_word.png')
  st.image(Image.open('most_common_word.png'))

with d2:
  # Create the WordCloud
  comment_words = ''
  
  # Iterate through the dataframe
  for val in df['preprocessed_text'].values:
    # Typecaste each val to string
    val = str(val)

    # Split the value
    tokens = val.split()

    # Add the words to the list
    comment_words += " ".join(tokens)+" "
  
  wordcloud = WordCloud(width = 800, height = 800,
                  background_color ='white',
                  stopwords = id_stop,
                  min_font_size = 10).generate(comment_words)
  
  # Plot the WordCloud             
  plt.figure(figsize = (12, 8), facecolor = None)
  plt.imshow(wordcloud)
  plt.axis("off")
  plt.tight_layout(pad = 0)
  plt.savefig('word_cloud.png')
  st.image(Image.open('word_cloud.png'))

# MODELLING
# Apply Tfidf Vectorizer (count how many times do a word appear in a sentence)
text = df["preprocessed_text"].values

tfidf_vect = TfidfVectorizer()
tfidf_vect.fit_transform(text)

with open('Model/model.bin', 'rb') as f_in:
  logreg = pickle.load(f_in)

# Create a function to apply the model
sentiment_map = {0: "Mohon maaf atas ketidaknyamanannya ya :(", 
                  1: "Terima kasih atas masukan positifnya >o<"}

def predict_sentiment(review):
  review = preprocess_text(review)
  review = [review]
  review = tfidf_vect.transform(review)

  prediction = int(logreg.predict(review))
  sentiment = sentiment_map.get(prediction)

  return sentiment

# Predict sentiment
st.header("Berikan ulasanmu di sini!")
review_input = st.text_input("Tuliskan pengalaman menginap kamu!","Klik di sini...")
sentiment_analysis = predict_sentiment(review_input)
st.write(sentiment_analysis)
