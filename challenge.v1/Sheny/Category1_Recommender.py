import json
import os
import nltk.corpus
import nltk.tokenize.punkt
from nltk.tokenize import WhitespaceTokenizer
import nltk.stem.snowball
import string
import Levenshtein
from pymongo import MongoClient
from operator import itemgetter

from langdetect import detect
import codecs
import numpy

''' First thoughts on how to make recommendations to empty playlists given title of playlist only.   '''
cache={}


# For this to work an instance of MongoDB should be installed locally and be running.
def createMongoDB_songsCollection():
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    songs= db['songs-collection']
    path = "C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/song_popularity_sorted.json"; # modify the path to data
    f = open(path)
    js = f.read()
    f.close()
    data = json.loads(js)
    for song in data["songs"]:
        songs.insert_one(song)

    print(songs.count())
    print("Done")


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



def get_song(song_id):
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    songs= db['songs-collection']
    result= songs.find_one({"id": str(song_id)})
    if result is None: # no data could be found under this id
        print "No song found! "
        result={}
    return result

def get_popular_songs():
    f = open("C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/popular_songs.json")
    js = f.read()
    f.close()
    data = json.loads(js)
    return data

def empty_playlist_recommender(data):
    result= open("category_1_recommendations.csv", "w") #file for storing results
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
             similar_playlists.append(p[pid])

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
    #playlist_tracks= playlist["tracks"]
    number_of_rec=500
    song_list={} # for storing the recommendations

    array_songs=[] # array for storing songs of similar playlists
    total_songs=0
    for p in similar_playlists:
        if len(song_list) < number_of_rec :
            for song in p['tracks']:
                if song["track_uri"] not in song_list and len(song_list) < number_of_rec: #  and track_exists(playlist_tracks,song["track_uri"])!= 1 not needed because playlists are empty!!
                    song_list[song["track_uri"]]= song["track_uri"]
        else:
            break

    #sort recommendations by popularity
    #sorted_song_list= sorted(array_songs, key=itemgetter('frequency'), reverse=True)

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

def get_playlist_object(pid):
    if pid >=0 and pid < 1000000:
        low = 1000 * int(pid / 1000)
        high = low + 999
        offset = pid - low
        # ADAPT PATH TO THE DATA
        path = "C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/all/mpd.slice." + str(low) + '-' + str(high) + ".json"
        f = codecs.open(path, 'r', 'utf-8')
        js = f.read()
        f.close()
        playlist = json.loads(js)
        return playlist['playlists'][offset]



def get_playlist_data():
    p= numpy.load("playlist_data.npy").item()
    return p


if __name__ == '__main__':
    f = open("../challenge_1.json")
    js = f.read()
    f.close()
    data = json.loads(js)

    empty_playlist_recommender(data)



    '''
    file = open("playlist_ids.csv")
    line= file.readline()
    pids=[] # Array containing reduced set of playlists ids
    p_title={}
    while line:
        if line != '':
            id= int(line)
            pids.append(id)
        line= file.readline()
    count - 0    
    for pid in pids:
        print pid
        playlist= get_playlist_object(pid)
        p_title[pid]={"name" : playlist["name"], "tracks" : playlist["tracks"]}

    numpy.save('playlist_data.npy', p_title)
    print "FINISHED"
    '''
