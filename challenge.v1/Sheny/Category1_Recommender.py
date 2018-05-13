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

''' First thoughts on how to make recommendations to empty playlists given title of playlist only.   '''

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
    # Get default English stopwords and extend with punctuation
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.extend(string.punctuation)
    stopwords.append('')

    #PENDING: FILTER OUT EMOJIS

    # Create tokenizer and stemmer
    tokenizer= WhitespaceTokenizer()
    stemmer = nltk.stem.snowball.SnowballStemmer('english')

    # process title of first playlist
    temp_t1= tokenizer.tokenize(t1)
    tokens_t1=[]
    for token in temp_t1:
        if token.lower().strip(string.punctuation) not in stopwords:
            tokens_t1.append(
                token.lower().strip(string.punctuation))

    stems_t1= [stemmer.stem(token) for token in tokens_t1]

    # process title of second playlist
    temp_t2= tokenizer.tokenize(t2)
    tokens_t2=[]
    for token in temp_t2:
        if token.lower().strip(string.punctuation) not in stopwords:
            tokens_t2.append(
                token.lower().strip(string.punctuation))

    stems_t2= [stemmer.stem(token) for token in tokens_t2]

    # Calculate Jaro-Winkler distance
    distance = Levenshtein.jaro_winkler(''.join(stems_t1), ''.join(stems_t2))
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
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    songs= db['songs-collection']
    return songs.find().sort('frequency', -1).limit(1000) # sort songs based on frequency value



def empty_playlist_recommender(data):
    path = "C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/all"; # modify the path to mpd data
    filenames = os.listdir(path)
    result= open("category_1_recommendations.csv", "w") #file for storing results
    for challenge_p in data['playlist']:
         similar_playlists=[]
         for filename in sorted(filenames):
                if filename.startswith("mpd.slice.") and filename.endswith(".json"):
                    fullpath = os.sep.join((path, filename))
                    f = open(fullpath)
                    js = f.read()
                    f.close()
                    mpd_slice = json.loads(js)
                    for mpd_p in mpd_slice['playlists']:
                        similarity= similarity_titles(challenge_p["name"], mpd_p["name"])
                        threshold=0.7
                        if similarity > threshold:
                            mpd_p["similarity"] = similarity
                            similar_playlists.append(mpd_p)

         r_s=""
         for p in similar_playlists:
             r_s=r_s+ "\t" +str(p["name"])
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
    playlist_tracks= playlist["tracks"]
    number_of_rec=50
    song_list={} # for storing the recommendations

    array_songs=[] # array for storing songs of similar playlists
    for p in similar_playlists:
        for song in p['tracks']:
            song_info=get_song(song['track_uri'])
            array_songs.append(song_info)

    #sort recommendations by popularity
    sorted_song_list= sorted(array_songs, key=itemgetter('frequency'), reverse=True)
    for song in sorted_song_list:
        song_list[str(song['id'])]= str(song['id'])

    print(len(song_list))
    print(song_list)

    # if not enough songs were collected, recommend popular songs
    while len(song_list) < number_of_rec:
        for song in get_popular_songs():
            track= song['id']
            if track not in song_list and track_exists(playlist_tracks,track)!= 1: # check condition **
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




if __name__ == '__main__':
    path = "C:/Users/sheny/Desktop/SS 2018/LUD/Project/challenge/c1_sample.json"; # modify the path to data
    f = open(path)
    js = f.read()
    f.close()
    data = json.loads(js)

    empty_playlist_recommender(data)


