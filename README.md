# Recommendation System
Unsupervised Learning Project

### Three Recommendation Type:
<ul>
  <li>Section A: Movie based</li>
  <li>Section B: Person based(cast Member)</li>
  <li>Section C: genres based</li>
</ul>

## Section A: Movie based

In this user can select number of recommendation they wants related to a specific Movie selected by movie name.

### Four Algorithm Type:
<ul>
  <li>Section A.1: Content Based (TF-IDF)</li>
  <li>Section A.2: Content Based (Bag Of Words)</li>
  <li>Section A.3: Item-Item Collaborative Based</li>
  <li>Section A.4: K Nearest Neighbor (Item Based)</li>
</ul>

### Section A.1: Content Based (TF-IDF)

This Algorithm used TfidfVectorizer for vector conversion and Cosine Similarity for calculating angle between two vector. On the basis of movie name selected by user this Algorithm retrun list of movies sorted in descending order with respect to similarity which is taken from similarity matrix(contains similarity score for each movies ) 
Code: <a href="https://github.com/shivam1808/Recommendation-System/blob/master/Recommender%20Systems%20with%20Python.ipynb">Recommender Systems with Python.ipynb</a>

### Section A.2: Content Based (Bag Of Words)

Bag of Words is same techique as TF-IDF but in this score is calculating on the basis of frequency of most repetative words in content of moveis ans here similarity score is also calculating in same way as in TF-IDF
Code:
<a href="https://github.com/shivam1808/Recommendation-System/blob/master/Recommender%20Systems%20with%20Python.ipynb">Recommender Systems with Python.ipynb</a>

### Section A.3: Item-Item Collaborative Based

In this Algorithm a user ratings for sepcific movie is calculating on the basis of how other movies rated by same user and by taking some real time rartings we can show recommendation to users
<a href="https://github.com/shivam1808/Recommendation-System/blob/master/Recommender%20Systems%20with%20Python.ipynb">Recommender Systems with Python.ipynb</a>

### Section A.4: K Nearest Neighbor (Item Based)

User ratings here also predicted same as in Item-Item Collaborative filtering but for calculating distance it usses euclidean and manhattan distance between to vector and according to that form a similarity matrix, then show recomendation to user with respect to a specific movie which is selected by user
<a href="https://github.com/shivam1808/Recommendation-System/blob/master/Recommender%20Systems%20with%20Python.ipynb">Recommender Systems with Python.ipynb</a>



## Section B: Person based(cast Member)

User can also get recommendation on the basis of a person which casted in movies as lead actors or director.

Firslty all movies in which that person is casted as actor or director is sorted in reverse order according to the average rating and if number of recommendation is greater than that person's movies then user get recommendation on the basis of first movie which is going to be recommended first to user
<a href="https://github.com/shivam1808/Recommendation-System/blob/master/Recommender%20Systems%20with%20Python.ipynb">Recommender Systems with Python.ipynb</a>


## Section C: genres based

This recomendation is based on those movies which has same genres as selected by user and then sorted in reverse order according to average ratings of each movie
<a href="https://github.com/shivam1808/Recommendation-System/blob/master/Recommender%20Systems%20with%20Python.ipynb">Recommender Systems with Python.ipynb</a>


# Installation

`pip install -r requirements.txt`

# Set Up

`streamlit run main.py`

