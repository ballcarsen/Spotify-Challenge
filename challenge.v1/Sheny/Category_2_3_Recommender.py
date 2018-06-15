import json

import nltk.corpus
import nltk.tokenize.punkt
from nltk.tokenize import WhitespaceTokenizer
import nltk.stem.snowball
import string
import Levenshtein
from operator import itemgetter

from langdetect import detect
import codecs
import numpy

''' Proposal on how to make recommendations to  playlists given 1 or 5 songs only.   '''


def similarity_titles(t1, t2):

    # General tokenizer
    tokenizer= WhitespaceTokenizer()
    #English  NLP elements
    stopwords = nltk.corpus.stopwords.words('english')
    extra_en=['edit','feat', 'remix', 'mix', 'spotify', 'song', 'track', 'bonus', 'vs', 'best', 'remastered', 'album', 'ft', 'best', 'playlist', 'version']
    extra_es= ['editado', 'canci\u00F3n', 'cancion', 'mejor','dueto']
    stopwords.append('')
    stopwords = stopwords + extra_en + extra_es

    temp_t1= tokenizer.tokenize(t1)
    tokens_t1=[]
    for token in temp_t1:
        if token.lower().strip(string.punctuation) not in stopwords:
            tokens_t1.append(token.lower().strip(string.punctuation))

    temp_t2= tokenizer.tokenize(t2)
    tokens_t2=[]
    for token in temp_t2:
        if token.lower().strip(string.punctuation) not in stopwords:
            tokens_t2.append(token.lower().strip(string.punctuation))
    distance=0;
    if len(tokens_t1) != 0 and len(tokens_t2) != 0:
        distance = Levenshtein.jaro_winkler(''.join(tokens_t1), ''.join(tokens_t2))
    return distance


def get_popular_songs():
    f = open("C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/popular_songs.json")
    js = f.read()
    f.close()
    data = json.loads(js)
    return data

def get_BoW_clusters():
    bow = numpy.load('BoW_clusters.npy').item()
    return bow

def get_similarity(challenge_w, cluster_w):
    common_elems=len(set(challenge_w).intersection(cluster_w))
    total_elems= len(challenge_w) + len(cluster_w) - common_elems
    return common_elems/float(total_elems)

def get_words_challenge(challenge_p):
    stems_sq=[]

    #English  NLP elements
    stopwords_en = nltk.corpus.stopwords.words('english')
    stopwords_en.extend(string.punctuation)
    extra_en=['edit','feat', 'remix', 'mix', 'spotify', 'song', 'track', 'bonus', 'vs', 'best', 'remastered', 'album', 'ft', 'best', 'my', 'version']
    stopwords_en.append('')
    stopwords_en = stopwords_en + extra_en
    #Create stemmer for English songs
    stemmer_en = nltk.stem.snowball.SnowballStemmer('english')

    #Spanish NLP elements
    extra_es= ['edit', 'editado','remix', 'mix', 'canci\u00F3n', 'cancion', 'mejor', 'album', 'spotify', 'feat', 'dueto', 'bonus', 'ft', 'version']
    stopwords_es= nltk.corpus.stopwords.words('spanish')
    stopwords_es.extend(string.punctuation)
    stopwords_es.append('')
    stopwords_es= stopwords_es + extra_es
    # Create stemmer for Spanish songs
    stemmer_es = nltk.stem.snowball.SnowballStemmer('spanish')

    # General tokenizer
    tokenizer= WhitespaceTokenizer()
    seq = challenge_p["name"]
    for track in challenge_p["tracks"]:
        seq= seq + " "+ track["track_name"]+" "+ track["album_name"]

    try:
        lang= detect(seq)
    except:
        lang="undefined"

    if lang == "es":
        # process title of track and album
        sequence = seq.lower()
        temp_sq = tokenizer.tokenize(sequence)
        tokens_sq =[]
        for token in temp_sq:
            if token.strip(string.punctuation) not in stopwords_es:
                tokens_sq.append(token.strip(string.punctuation))

        stems_sq= [stemmer_es.stem(token) for token in tokens_sq]

    if lang == "en":
        # process title of track
        sequence = seq.lower().lower()
        temp_sq = tokenizer.tokenize(sequence)
        tokens_sq=[]
        for token in temp_sq:
             if token.strip(string.punctuation) not in stopwords_en:
                 tokens_sq.append(token.strip(string.punctuation))

        stems_sq= [stemmer_en.stem(token) for token in tokens_sq]

    return stems_sq

def short_songs_playlist_recommender(data):
    result = open("category_2_recommendations.csv", "w") #file for storing results
    bow = get_BoW_clusters()
    p = get_playlist_data()
    count = 0
    for challenge_p in data['songs']:
         similar_playlists=[]
         count += 1
         print count
         max_sim=0
         max_cluster_words={}
         challenge_words= get_words_challenge(challenge_p)
         print challenge_words
         for cluster in bow:
            words= bow[cluster]
            similarity= get_similarity(challenge_words, words.keys())
            if similarity > max_sim:
                max_sim= similarity
                max_cluster_words= words

         print max_sim
         # get words of union both sets
         intersection= set(challenge_words).intersection(max_cluster_words.keys())
         print intersection
         # get playlists of these words and add to similar playlist list
         for word in intersection:
             for pid in max_cluster_words[word]:
                 print pid
                 similar_playlists.append(p[pid])# append playlist object


         print similar_playlists
         make_500_recommendations(challenge_p, similar_playlists, result)

    result.close()
    print ("***** Finished ******")


def track_exists(playlist_tracks, track):
    if(len(playlist_tracks) == 0):
        return -1
    else:
        for current in playlist_tracks:
            if(current["track_uri"] == track):
                return 1
        return -1

''' Recommend songs of playlists with similar titles. If not enough songs are collected popular songs will be added to the result.  '''
def make_500_recommendations(playlist, similar_playlists, result_f):
    playlist_id= playlist["pid"]
    number_of_rec=500
    song_list={} # for storing the recommendations
    array_songs=[] # array for storing songs of similar playlists
    total_songs=0
    for p in similar_playlists:
        if len(song_list) < number_of_rec:
            tracks= p['tracks']
            if p["num_followers"] < 10:
                #SORT SONGS BASED ON POPULARITY
                tracks= sorted(p['tracks'], key=itemgetter('frequency'), reverse=True)
            for song in tracks:
                if song["track_uri"] not in song_list and len(song_list) < number_of_rec: #  and track_exists(playlist_tracks,song["track_uri"])!= 1 not needed because playlists are empty!!
                        song_list[song["track_uri"]]= song["track_uri"]
        else:
            break


    popular_songs= get_popular_songs()
    # if not enough songs were collected, recommend popular songs
    while len(song_list) < number_of_rec:
        for song in popular_songs["songs"]:
            track= song['id']
            if track not in song_list: # and track_exists(playlist_tracks,track)!= 1  not needed because playlists are empty!!
                song_list[str(track)]= track

    # write recommendations to result file
    keys=song_list.keys()
    i=0
    result_string=""
    while i < len(keys):
        if i == len(keys)-1:
            result_string= result_string + song_list[keys[i]] + "\n"
        else:
            result_string= result_string + song_list[keys[i]] + ","
        i= i +1

    line= str(playlist_id)+ "," + result_string
    result_f.write(line.encode("utf8"))



def get_playlist_data():
    p= numpy.load("playlist_data.npy").item()
    return p


if __name__ == '__main__':
    path= "../challenge_2.json"
    f= open(path)
    js = f.read()
    f.close()
    data = json.loads(js)
    short_songs_playlist_recommender(data)



