import json
import os
from operator import itemgetter
from pymongo import MongoClient
import math
import numpy
import codecs


cache={}


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

# Simple function for ordering songs by their frequency.
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
def convert_playlist_to_vector(path):
    filenames = os.listdir(path)
    playlist_c = open("playlist_vectors.csv", "w")
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
                    result= analyze_playlist(playlist)
                    vector= get_vector_of_playlist2(result)
                    vect_string= ','.join(str(x) for x in vector)
                    playlist_c.write(str(playlist['pid']) +","+ vect_string +"\n" )
                    fileNum = fileNum + 1
            print fileNum
    playlist_c.close()
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
                vector = get_vector_of_playlist2(vector)
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


# Function that returns the reduced set of artist (i.e. artists with more than 10 songs in 1 million playlists.
# Every entry in  the dictionary is identified by the artist id.
# The value stored is the total number of playlist containing the artist and the predefined index of that artist (for the vector representation of the playlists).
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
        totalNumberOfPlaylists = reduced_artist[artist['artist']]['numberPlaylist'] # get total number of playlists containing this artist
        songNum = artist['numSongs'] # get the number of songs in current playlist of artist
        numberPlaylists =1000000 # fix number of playlist in data set
        # compute tf_idf of artist
        tfidf = (1 + math.log(songNum))* math.log(numberPlaylists/ totalNumberOfPlaylists)
        array[index] = tfidf # store weight of artist in vector
    return array

def track_exists(playlist_tracks, track):
    if(len(playlist_tracks) == 0):
        return -1
    else:
        for current in playlist_tracks:
            if(current["track_uri"] == track):
                return 1
        return -1

# function for searching a playlist given its id
def get_playlist_object(pid):
    if pid >=0 and pid < 1000000:
        low = 1000 * int(pid / 1000)
        high = low + 999
        offset = pid - low
        # ADAPT PATH TO THE DATA
        path = "C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/all/mpd.slice." + str(low) + '-' + str(high) + ".json"
        if not path in cache:
            f = codecs.open(path, 'r', 'utf-8')
            js = f.read()
            f.close()
            playlist = json.loads(js)
            cache[path] = playlist

        playlist = cache[path]['playlists'][offset]
        return playlist


def create_song_collection():
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    songs= db['song-collection']
    songs.create_index("song_id", unique=True)

    path= "C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/song_popularity_sorted.json"
    f= open(path)
    js = f.read()
    f.close()
    data = json.loads(js)

    for song in data["songs"]:
        print song["id"]
        print song["frequency"]
        data= {"song_id" : song["id"], "frequency": song["frequency"]}
        #STORE VALUES IN DB
        songs.insert_one(data)
    print songs.count()
    print "Finished"


def get_song_frequency(id):
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    songs= db['song-collection']
    result=songs.find_one({"song_id": id})
    if result is None:
        return -1
    return result["frequency"]


if __name__ == '__main__':

    path= "C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/all"
    convert_playlist_to_vector(path)

