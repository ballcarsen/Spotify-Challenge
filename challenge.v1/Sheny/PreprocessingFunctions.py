import json
import os
from operator import itemgetter
from pymongo import MongoClient
import math

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

def get_MongoDB_playlistCollection():
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    playlist_c= db['playlists-collection']
    return playlist_c

def reset_MongoDB_playlistCollection():
    client= MongoClient('localhost', 27017)
    db= client['spotify-challenge']
    playlist_c= db['playlists-collection']
    playlist_c.remove({})

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

# Main function for computing the  vector representation of the playlists.
# This function stores the vector in the playlists-collection
def convert_playlist_to_vector(path):
    filenames = os.listdir(path)
    playlist_data={}
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            print("Playlist ",  filename)
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            mpd_slice = json.loads(js)
            for playlist in mpd_slice['playlists']:
                artists= analyze_playlist(playlist)
                playlist_data[playlist['pid']]={'pid':playlist['pid'], 'vector': artists}

    playlist_c= get_MongoDB_playlistCollection()
    keys= playlist_data.keys()
    i=0
    print('writing results to DB ')
    while i < len(keys):
        playlist= playlist_data[keys[i]]
        playlist_c.insert_one({'pid': playlist['pid'] , 'vector': get_vector_of_playlist(playlist['vector'])})
        i= i+1
    print("FINISHED")

    '''
    print('writing results to file ')
    result = open("playlist_vectors.csv","w")
    keys= playlist_data.keys()
    i=0
    while i < len(keys):
        playlist= playlist_data[keys[i]]
        line= str(playlist['pid'])+","+ get_vector_as_string(playlist['vector'])+'\n'
        result.write(line)
        i= i+1
    result.write('\n')    
    result.close()
    '''

# Function for analyzing a playlist in terms of artist occurrence.
# It will return an array where every row contains the artistId and the number of songs of the artist in the playlist.
def analyze_playlist(playlist):
    artists={}
    for i, track in enumerate(playlist['tracks']):
        artist_id = track['artist_uri']
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
    numberOfArtists=295860
    array = array * numberOfArtists # creating array of correct size
    i= 0
    while i < numberOfArtists:
        array[i]= 0 #populating array with 0's
        i = i + 1

    for artist in artists:
        index= get_index(artist['artist'])
        songNum= artist['numSongs']
        numberPlaylists=1000000
        # compute tfidf of artist
        tfidf= (1 + math.log(songNum))* math.log(numberPlaylists/ get_number_songs(artist['artist']))
        print (index, tfidf)
        array[index]= tfidf
    return array

if __name__ == '__main__':
    path = "C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/all"; # modify the path to data
    convert_playlist_to_vector(path)


