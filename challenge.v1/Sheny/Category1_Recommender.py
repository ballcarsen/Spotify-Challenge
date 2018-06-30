# coding=utf-8
import json
import nltk.corpus
import nltk.tokenize.punkt
from nltk.tokenize import WhitespaceTokenizer
import nltk.stem.snowball
import string
import Levenshtein
from operator import itemgetter
import numpy




''' Proposal on how to make recommendations to empty playlists given title of playlist only and palylists with 5 songs.   '''

''' Based on ideas presented in https://bommaritollc.com/2014/06/30/advanced-approximate-sentence-matching-python/  '''
def similarity_titles(t1, t2):
    # WE CANNOT DO NLP BECAUSE LANGUAGE DETECTION IS NOT ACCURATE FOR VERY SHORT TEXTS (< 3 words)

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

''' Opens a json file containing the first 600 popular songs. The songs are ordered by popularity in DESC order. '''
def get_popular_songs():
    f = open("C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/popular_songs.json")
    js = f.read()
    f.close()
    data = json.loads(js)
    return data

''' Main method for making recommendations. The parameter passed has to be the json object of the challenge playlists. 
    It will compute 500 songs for each of the challenge playlists based on title similarity to the reduced data set of playlists. '''
def empty_playlist_recommender(data):
    result= open("result_recommendations.csv", "w") #file for storing results
    p= get_playlist_data()
    print "Loaded playlists into memory..."
    count = 0
    for challenge_p in data['songs']:
         similar_playlists=[]
         temp={} # dictonary for storing playlist id and similarity rate
         count += 1
         print count
         for pid in p:
            playlist= p[pid]
            similarity= similarity_titles(challenge_p["name"], playlist["name"])
            threshold=0.7
            if similarity > threshold:
                temp[pid]= similarity
         #sort playlists based on similarity
         new_list= sorted(temp.items(), key=itemgetter(1), reverse=True)
         for playlist in new_list:
             pid= playlist[0]
             similar_playlists.append(p[pid])# append playlist object

        # PROCEED TO MAKE RECOMMENDATIONS
         make_500_recommendations(challenge_p, similar_playlists, result)

    result.close()

''' Simple method for checking if a given song is present in a playlist.
    Returns 1 if the song exists on the playlist tracks, otherwise it returns -1. '''
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
    for p in similar_playlists:
        if len(song_list) < number_of_rec:
            #SORT SONGS BASED ON POPULARITY
            tracks= sorted(p['tracks'], key=itemgetter('frequency'), reverse=True)
            for song in tracks:
                if song["track_uri"] not in song_list and len(song_list) < number_of_rec and track_exists(playlist['tracks'], song["track_uri"]) != 1:
                        song_list[song["track_uri"]] = song["track_uri"]
        else:
            break

    popular_songs= get_popular_songs()
    # if not enough songs were collected, recommend popular songs
    if len(song_list) < number_of_rec:
        for song in popular_songs["songs"]:
            track= song['id']
            if len(song_list) < number_of_rec and track not in song_list and track_exists(playlist['tracks'], track) != 1 :
                song_list[str(track)] = track

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

''' Method for returning a dictonary containing the reduced playlist set. 
    Every entry in the dictonary is identified by the playlist id.  
    The value stored is an array of the id of the tracks of the playlist and the popularity of the song. '''
def get_playlist_data():
    p= numpy.load("playlist_data.npy").item()
    return p

if __name__ == '__main__':
    path= "../challenge_1_3.json"
    f= open(path)
    js = f.read()
    f.close()
    data = json.loads(js)
    empty_playlist_recommender(data)



