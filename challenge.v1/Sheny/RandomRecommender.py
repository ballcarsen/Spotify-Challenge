import json
import random

'''The aim of this file is to show how to build a submission file for the Spotify Challenge. 
   It takes approx. 3 hours to build the dummy recommendation file. '''

def random_recommender(data, result, index, end):
     while index< end:
         print (index)
         make_500_recommendations(data['playlists'][index]["pid"], data['playlists'][index]["tracks"], result)
         index= index +1
     result.close()
     print ("******************** Finished ************************")


def track_exists(playlist_tracks, track):
    if(len(playlist_tracks) == 0):
        return -1
    else:
        for current in playlist_tracks:
            if(current["track_uri"] == track):
                return 1
        return -1

''' This approach leads to poor results as the order of the recommendations also plays an important role.  '''
def make_500_recommendations(playlist_id, playlist_tracks, result_f):
    f_popular_songs= open("songs_popular_playlists.json","r")
    string_js = f_popular_songs.read()
    f_popular_songs.close()
    popular_songs = json.loads(string_js)
    number_of_rec=500
    song_list={} # for storing recommended songs
    while len(song_list) < number_of_rec:
        index= random.randint(0, len(popular_songs["songs"])-1)
        while index in song_list or track_exists(playlist_tracks,popular_songs["songs"][index]['id'])==1:
            #need a new index
            index= random.randint(0, len(popular_songs["songs"])-1)

        song_list[str(index)]= popular_songs["songs"][index]['id']

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
    path = "C:/Users/sheny/Desktop/SS 2018/LUD/Project/challenge/challenge_set.json"; # modify the path to data
    f = open(path)
    js = f.read()
    f.close()
    data = json.loads(js)
    start=0
    end=len(data['playlists'])
    result=open("random_recommendations.csv", "w")
    random_recommender(data, result, start, end)

