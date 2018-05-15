import json
import os
from operator import itemgetter

# Main function for computing the frequency of all songs in the data set.
# It will create a json file containing the song information and its frequency.
# The list of songs will be unsorted.
def process_playlists(path):
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

                analyze_playlist(playlist,song_data)

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



# Function for storing and incremeneting the song's frequency
def analyze_playlist(playlist,song_data):
    for i, track in enumerate(playlist['tracks']):
        song_id = track['track_uri']
        if(song_id in song_data): #increment frequency
            temp=song_data[song_id]
            temp['frequency']= temp['frequency'] + 1
            song_data[song_id]= temp
        else:
            song_data[song_id]={"id": song_id, "name": track['track_name'], "artist":track['artist_name'], "frequency": 1}



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
    path = "C:/Users/sheny/Desktop/SS 2018/LUD/Project/mpd/data/all"; # modify the path to data
    process_playlists(path)
    order_by_popularity()

