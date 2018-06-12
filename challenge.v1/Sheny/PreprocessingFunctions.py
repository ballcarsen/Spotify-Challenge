import json
import os
from operator import itemgetter
from pymongo import MongoClient
import math
import numpy

import collections
from langdetect import detect
import nltk.corpus
import nltk.tokenize.punkt
import string
from nltk.tokenize import WhitespaceTokenizer
import nltk.stem.snowball

# Main function for computing the frequency of all songs in the data set.
# It will create a json file containing the song information and its frequency.
# The list of songs will be unsorted.
def get_song_frequency(path):
    filenames = os.listdir(path)
    song_data={}
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            print("Playlist ",  filename)
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            mpd_slice = json.loads(js)
            for playlist in mpd_slice['playlists']:
                analyze_playlist_by_song(playlist, song_data)

    result = open("song_popularity.json","w")
    result.write('{\n \t "songs": [ \n')
    max_keyNum=len(song_data.keys())
    count=1
    for key in song_data.keys():
        if(count != max_keyNum):
            line="\t\t"+json.dumps(song_data[key])+","+'\n'
        else:
            line="\t\t"+json.dumps(song_data[key])+'\n'
        result.write(line)
        count= count + 1

    result.write('\t ] \n } \n')
    print("FINISHED");
    result.close()

# Naive and simple function for ordering songs by their frequency.
# It will create a new json file with the list of songs sorted by their frequency in descending order.
def order_by_popularity():
    f_popular_songs= open("song_popularity.json","r")
    string_js = f_popular_songs.read()
    f_popular_songs.close()
    popular_songs = json.loads(string_js)
    array_songs=popular_songs["songs"]

    new_list= sorted(array_songs, key=itemgetter('frequency'), reverse=True)
    result = open("song_popularity_sorted.json","w")
    result.write('{\n \t "songs": [ \n')
    max_Num= len(new_list)
    count=1
    for song in new_list:
        if(count != max_Num):
            line="\t\t"+json.dumps(song)+","+'\n'
        else:
            line="\t\t"+json.dumps(song)+'\n'

        result.write(line)
        count= count + 1

    result.write('\t ] \n } \n')
    print("FINISHED");
    result.close()

# Main function for collecting artist information
def get_artist_info(path):
    filenames = os.listdir(path)
    artist_data={}
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            print("Playlist ",  filename)
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            mpd_slice = json.loads(js)
            for playlist in mpd_slice['playlists']:
                analyze_playlist_by_artist(playlist, artist_data)

    result = open("artist_info.json","w")
    result.write('{\n \t "artists": [ \n')
    max_keyNum=len(artist_data.keys())
    count=1
    for key in artist_data.keys():
        if count != max_keyNum:
            line="\t\t"+json.dumps(artist_data[key])+","+'\n'
        else:
            line="\t\t"+json.dumps(artist_data[key])+'\n'
        result.write(line)
        count= count + 1

    result.write('\t ] \n } \n')
    result.close()



# Function for storing/updating the artist information (id, name, numberOfSongs, index)
def analyze_playlist_by_artist(playlist, artist_data):
    for i, track in enumerate(playlist['tracks']):
        artist_id = track['artist_uri']
        if(artist_id in artist_data): #increment frequency
            temp=artist_data[artist_id]
            temp['numberOfSongs']= temp['numberOfSongs'] + 1
            artist_data[artist_id]= temp
        else:
            artist_data[artist_id]={"id": artist_id, "name": track['artist_name'], "numberOfSongs": 1, "index": len(artist_data.keys())}

# Function for creating artist collection
def createMongoDB_artistCollection():
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    artists= db['artists-collection']
    f = open("artist_info.json")
    js = f.read()
    f.close()
    data = json.loads(js)
    for artist in data["artists"]:
        artists.insert_one(artist)
    print(artists.count())
    print("Done")

# Function for storing and incremeneting the song's frequency
def analyze_playlist_by_song(playlist, song_data):
    for i, track in enumerate(playlist['tracks']):
        song_id = track['track_uri']
        if(song_id in song_data): #increment frequency
            temp=song_data[song_id]
            temp['frequency']= temp['frequency'] + 1
            song_data[song_id]= temp
        else:
            song_data[song_id]={"id": song_id, "name": track['track_name'], "artist":track['artist_name'], "frequency": 1}

''' FUNCTIONS FOR VECTOR TRANSFORMATION '''
def get_MongoDB_playlistCollection():
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    playlist_c= db['playlists-collection']
    return playlist_c

def reset_MongoDB_playlistCollection():
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    playlist_c= db['playlists-collection']
    playlist_c.drop()

# Function for returning the index of an artist given its id
def get_index(artist_id):
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    songs= db['artists-collection']
    result= songs.find_one({"id": str(artist_id)})
    if result is None: # no data could be found under this id
        print "No artist found!"
        result={}
    return result['index']

# Function for returning the number of songs -in the whole playlist set- of an artist given its id
def get_number_songs(artist_id):
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    songs= db['artists-collection']
    result= songs.find_one({"id": str(artist_id)})
    if result is None: # no data could be found under this id
        print "No artist found!"
        result={}
    return result['numberOfSongs']


# Function for returning the vector representation of a playlist given its id
def get_playlist_vector(pid):
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    playlists= db['playlists-collection']
    result= playlists.find_one({"pid": pid})
    if result is None: # no data could be found under this id
        print "No playlist found!"
        result={}
    return result

# Main function for computing the  vector representation of the playlists.
# This function stores the vector in the playlists-collection
def convert_playlist_to_vector(path):
    filenames = os.listdir(path)
    playlist_c = get_MongoDB_playlistCollection()
    fileNum=0
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            print("Playlist ",  filename)
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            mpd_slice = json.loads(js)
            for playlist in mpd_slice['playlists']:
                if playlist['num_followers'] >= 10: # we will only analyze  playlists with more than 9 followers
                    print (playlist['pid'])
                    vector= analyze_playlist(playlist)
                    playlist_c.insert_one({'pid': playlist['pid'] , 'vector': get_vector_of_playlist(vector)})
                    fileNum = fileNum + 1
            print fileNum
    print("FINISHED")


def convert_challenge_playlist_to_vector(filename):
    with open (filename, 'r') as challenge_file:
        with open("challenge_10_vector.csv", "w") as out:
            js = challenge_file.read()
            challenge = json.loads(js)
            count = 1

            for playlist in challenge['songs']:
                print (str(playlist['pid']) + ' ' + str(count))
                count += 1
                vector = analyze_playlist(playlist)
                vector = get_vector_of_playlist(vector)
                vector = numpy.array(vector)
                out.write(str(playlist['pid']) + ", ")

                for i in  range(len(vector)):
                    if i == len(vector) - 1:
                        out.write(str(vector[i]) + "\n")
                    else:
                        out.write(str(vector[i]) + ", ")
    print("FINISHED")

def store_reduced_artists():
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    playlist_c= db['artists-collection']
    result=playlist_c.find({'numberOfSongs' : {'$gte': 10}})
    artist={}
    print "working on it, please wait..."
    for p in result:
        artist[p['id']]= {'numberOfSongs': p['numberOfSongs'], 'index': len(artist.keys())}
    print "finished"
    numpy.save('artist_dic.npy', artist)

def get_reduced_artists():
    artists = numpy.load('artist_dic.npy').item()
    return artists


# Function for analyzing a playlist in terms of artist occurrence.
# It will return an array where every row contains the artistId and the number of songs of the artist in the playlist.
def analyze_playlist(playlist):
    artists= {}
    reduced_artist = get_reduced_artists()
    for i, track in enumerate(playlist['tracks']):
        artist_id = track['artist_uri']
        if artist_id in reduced_artist: #artist exist in our reduced set
            if artist_id in artists: #increment number of songs
                temp=artists[artist_id]
                temp['numSongs']= temp['numSongs'] + 1
                artists[artist_id]= temp
            else:
                artists[artist_id]={"artist":track['artist_uri'], "numSongs": 1}
    array=[]
    for i in artists.keys():
        array.append(artists[i])
    return array




def get_vector_of_playlist(artists):
    '''' Initializing array for storing vector values '''
    array=[None]
    numberOfArtists=86069 # EQUAL TO NUMBER OF ARTISTS WITH >=10 SONGS
    array = array * numberOfArtists # creating array of correct size
    i= 0
    while i < numberOfArtists:
        array[i]= 0 #populating array with 0's
        i = i + 1

    reduced_artist = get_reduced_artists()
    max_frequency = 0
    for artist in artists:
        if max_frequency < artist['numSongs']:
            max_frequency = artist['numSongs']

    for artist in artists:
        index = reduced_artist[artist['artist']]['index'] # get artist index from reduced set
        songNum = artist['numSongs'] # get the number of songs in current playlist of artist
        tf = songNum/ max_frequency
        array[index] = tf # store tf of artist in vector
    return array

def get_vector_of_playlist2(artists):
    '''' Initializing array for storing vector values '''
    array=[None]
    numberOfArtists=86069 # EQUAL TO NUMBER OF ARTISTS WITH >=10 SONGS
    array = array * numberOfArtists # creating array of correct size
    i= 0
    while i < numberOfArtists:
        array[i]= 0 #populating array with 0's
        i = i + 1

    reduced_artist = get_reduced_artists()

    for artist in artists:
        index = reduced_artist[artist['artist']]['index'] # get artist index from reduced set
        totalSongNum = reduced_artist[artist['artist']]['numberOfSongs'] # get total number of songs of the artist
        songNum = artist['numSongs'] # get the number of songs in current playlist of artist
        numberPlaylists =1000000 # fix number of playlist in data set
        # compute tf_idf of artist
        tfidf = (1 + math.log(songNum))* math.log(numberPlaylists/ totalSongNum)
        array[index] = tfidf # store weight of artist in vector
    return array




def get_common_words(playlist, top=15):
    result_string=""

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

    for track in playlist['tracks']:
        try:
            lang= detect(track['track_name'])
        except:
            lang='sth'
            #print "Could not determine language of ", track['track_name']

        if lang == 'es':

           # process title of track and album
            sequence = track['track_name'].lower() + ' ' + track['album_name'].lower()
            temp_sq = tokenizer.tokenize(sequence)
            #print temp_sq
            tokens_sq =[]
            for token in temp_sq:
                #print token.strip(string.punctuation)
                #print token.strip(string.punctuation) in stopwords_es
                if token.strip(string.punctuation) not in stopwords_es:
                    tokens_sq.append(token.strip(string.punctuation))

            stems_sq= [stemmer_es.stem(token) for token in tokens_sq]
            result_string= result_string +' ' + (' '.join(stems_sq))

        if lang == 'en':
            # process title of track
            sequence = track['track_name'].lower() + ' ' + track['album_name'].lower()
            temp_sq = tokenizer.tokenize(sequence)
            #temp_sq= tokenizer.tokenize(track['track_name'])
            tokens_sq=[]
            for token in temp_sq:
                if token.strip(string.punctuation) not in stopwords_en:
                    tokens_sq.append(token.strip(string.punctuation))

            stems_sq= [stemmer_en.stem(token) for token in tokens_sq]
            result_string= result_string +' ' + (' '.join(stems_sq))

        # else: # All other languages will be ignored!
        #

    words = collections.Counter(result_string.split()) # how often each word appears

    return dict(words.most_common(top))

def get_words_all_playlists(path):
    filenames = os.listdir(path)
    data={}
    for filename in sorted(filenames):

        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            print("Playlist ",  filename)
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            mpd_slice = json.loads(js)
            for playlist in mpd_slice['playlists']:
                 if playlist['num_followers'] >= 10:
                     pid= playlist['pid']
                     print pid
                     words=get_common_words(playlist)
                     data[pid]=words


    numpy.save('playlist_top_15_words.npy', data)
    print("FINISHED");


def get_playlist_top_15_words():
    playlists = numpy.load('playlist_top_15_words.npy').item()
    return playlists


def compute_BoW_clusters():
    file = open("../cluster_results_2.json", "r")
    data= file.read()
    file.close()
    clusters= json.loads(data)
    playlist = get_playlist_top_15_words()
    word_to_playlist={}
    for c in clusters["Clusters"]:
        words={}
        print "Cluster: ",c["Cluster"], len(c["data set playlists"])
        for pid in c["data set playlists"]:
            for w in playlist[pid]:
                if w not in words:
                    words[w]= [{"pid": pid, "frequency" : playlist[pid][w]}]
                else:
                    words[w].append({"pid": pid, "frequency" : playlist[pid][w]})
        # SORT AT THE END
        print "Sorting word array "
        for w in words:
            temp_sorted= sorted(words[w], key=itemgetter('frequency'), reverse=True)
            new_array=[]
            for i in temp_sorted:
                new_array.append(i['pid'])
            words[w]= new_array

        word_to_playlist[c["Cluster"]]=words


    numpy.save('BoW_clusters.npy', word_to_playlist)
    print "finished BoW of clusters"

def get_BoW_clusters():
    bow = numpy.load('BoW_clusters.npy').item()
    return bow

if __name__ == '__main__':
    # BUILD DICTONARY OF PLAYLISTS {pid: {word1: frequency, word2: frequency}}
    #path = "D:/LUD files/Project/mpd/data/all"; # modify the path to data
    #get_words_all_playlists(path)

    #compute_BoW_clusters()

    bow= get_BoW_clusters()
    for c in bow:
        print c, len(bow[c])

