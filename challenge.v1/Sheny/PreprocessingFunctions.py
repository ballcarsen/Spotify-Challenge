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
    title_string=""
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.extend(string.punctuation)
    stopwords.append('')

    # Create tokenizer and stemmer for English songs
    tokenizer= WhitespaceTokenizer()
    stemmer = nltk.stem.snowball.SnowballStemmer('english')

    for track in playlist['tracks']:
        lang= detect(track['track_name'])
        if lang == 'en':
            # process title of track
            temp_title= tokenizer.tokenize(track['track_name'])
            tokens_title=[]
            for token in temp_title:
                if token.lower().strip(string.punctuation) not in stopwords:
                    tokens_title.append(token.lower().strip(string.punctuation))

            stems_title= [stemmer.stem(token) for token in tokens_title]
            title_string= title_string +' ' + (' '.join(stems_title))

        else:
            title_string= title_string + ' '+ track['track_name']

    words = collections.Counter(title_string.split()) # how often each word appears
    return dict(words.most_common(top))

if __name__ == '__main__':
    playlist= {
            "name": "Fresh",
            "collaborative": "false",
            "pid": 334000,
            "modified_at": 1483833600,
            "num_tracks": 10,
            "num_albums": 8,
            "num_followers": 1,
            "tracks": [
                {
                    "pos": 0,
                    "artist_name": "Kstylis",
                    "track_uri": "spotify:track:0aWia6YqI2s9r41bXwnqhX",
                    "artist_uri": "spotify:artist:5o2jetVpyIsXvWDT27bN4k",
                    "track_name": "Booty Me Down",
                    "album_uri": "spotify:album:1NxzYCWWmlbipSTQa7hTRj",
                    "duration_ms": 212920,
                    "album_name": "Booty Me Down"
                },
                {
                    "pos": 1,
                    "artist_name": "Tyga",
                    "track_uri": "spotify:track:3xJj1mU7B83yop2dA03Smk",
                    "artist_uri": "spotify:artist:5LHRHt1k9lMyONurDHEdrp",
                    "track_name": "Bouncin On My D*ck",
                    "album_uri": "spotify:album:6xJC9AbMpm4ebrTWz6Fd5S",
                    "duration_ms": 195056,
                    "album_name": "#BitchImTheShit"
                },
                {
                    "pos": 2,
                    "artist_name": "Khia",
                    "track_uri": "spotify:track:1tc6RFcNQk2mQ0c0ZdiEBW",
                    "artist_uri": "spotify:artist:3q7isf09BuwXLyR2khBs60",
                    "track_name": "My Neck, My Back (Lick It) - Street/Club Version",
                    "album_uri": "spotify:album:2nIZvWCOoeVcjp5YV6XyLn",
                    "duration_ms": 221573,
                    "album_name": "My Neck, My Back (Lick It) - Remixes"
                },
                {
                    "pos": 3,
                    "artist_name": "The Pack",
                    "track_uri": "spotify:track:1NpcguIbdLR25tlymnwVVC",
                    "artist_uri": "spotify:artist:5M6GE2n46o0qBIyGXtzdQz",
                    "track_name": "Vans",
                    "album_uri": "spotify:album:4JbZYBoID3x3tLOEcrjD0G",
                    "duration_ms": 263800,
                    "album_name": "Skateboards 2 Scrapers EP"
                },
                {
                    "pos": 4,
                    "artist_name": "Beau Young Prince",
                    "track_uri": "spotify:track:6Nn6zvmdlXNBO1VwqaiCSw",
                    "artist_uri": "spotify:artist:5fxPQ2Mzi7apfCMPuKwmSd",
                    "track_name": "Half & Half Tea",
                    "album_uri": "spotify:album:6PuAwuUdBfPzYCPIKCn0Qv",
                    "duration_ms": 187895,
                    "album_name": "Until Then (feat. Yalamusiq)"
                },
                {
                    "pos": 5,
                    "artist_name": "Tommie Sunshine",
                    "track_uri": "spotify:track:4j4OnDsmAnTC71Nx2HaRns",
                    "artist_uri": "spotify:artist:42tlZWSz1V6Rsqds29GcRo",
                    "track_name": "Alright - Jesse Slayter Remix",
                    "album_uri": "spotify:album:4OfIb9WJ2PjajmPvIAhABG",
                    "duration_ms": 216253,
                    "album_name": "Alright"
                },
                {
                    "pos": 6,
                    "artist_name": "Kstylis",
                    "track_uri": "spotify:track:5w9uHCQaWsXVFMFr4TWlPx",
                    "artist_uri": "spotify:artist:5o2jetVpyIsXvWDT27bN4k",
                    "track_name": "Pretty Girl Twerk (feat. Nelly & Tiffany Foxx)",
                    "album_uri": "spotify:album:7355M9DGyWBqr3OH44e8PS",
                    "duration_ms": 191947,
                    "album_name": "Pretty Girl Twerk (feat. Nelly & Tiffany Foxx)"
                },
                {
                    "pos": 7,
                    "artist_name": "Big Sean",
                    "track_uri": "spotify:track:0SGkqnVQo9KPytSri1H6cF",
                    "artist_uri": "spotify:artist:0c173mlxpT3dSFRgMO8XPh",
                    "track_name": "Bounce Back",
                    "album_uri": "spotify:album:0XAIjjN5qxViVS0Y5fYkar",
                    "duration_ms": 222360,
                    "album_name": "I Decided."
                },
                {
                    "pos": 8,
                    "artist_name": "Tyga",
                    "track_uri": "spotify:track:20EACYL40C3BrrRJQ1P8sT",
                    "artist_uri": "spotify:artist:5LHRHt1k9lMyONurDHEdrp",
                    "track_name": "Mack Down",
                    "album_uri": "spotify:album:6xJC9AbMpm4ebrTWz6Fd5S",
                    "duration_ms": 238550,
                    "album_name": "#BitchImTheShit"
                },
                {
                    "pos": 9,
                    "artist_name": "Tyga",
                    "track_uri": "spotify:track:6GBooRCiR337B2ZQVB1e8T",
                    "artist_uri": "spotify:artist:5LHRHt1k9lMyONurDHEdrp",
                    "track_name": "Heisman",
                    "album_uri": "spotify:album:6xJC9AbMpm4ebrTWz6Fd5S",
                    "duration_ms": 138135,
                    "album_name": "#BitchImTheShit"
                }
            ],
            "num_edits": 6,
            "duration_ms": 2088489,
            "num_artists": 7
        }
    print get_common_words(playlist)





