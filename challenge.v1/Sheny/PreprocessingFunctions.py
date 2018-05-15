import json
import os
from operator import itemgetter
from pymongo import MongoClient

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

if __name__ == '__main__':
    #path = "C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/all"; # modify the path to data
    #get_artist_info(path)

    # 1. Start MongoDB server
    # 2. Execute this function
    #createMongoDB_artistCollection()

    # 3. Check that collection was filled
    print(get_index("spotify:artist:2ZDj97EXYJmMP9f6uce6zE")) # Result should be 243408





