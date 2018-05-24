import json
import random


def track_exists(playlist_tracks, track):
    if(len(playlist_tracks) == 0):
        return -1
    else:
        for current in playlist_tracks:
            if(current["track_uri"] == track):
                return 1
        return -1


def random_recommender_2(data, result, index, end):
    while index < end:
        print (index)
        make_500_recommendations(data['playlists'][index]["pid"], data['playlists'][index]["tracks"], result)
        index = index + 1
    result.close()
    print ("***** Finished ******")

def make_500_recommendations(playlist_id, playlist_tracks, result_f):
    f_popular_songs = open("song_popularity_sorted.json", "r")
    string_js = f_popular_songs.read()
    f_popular_songs.close()
    popular_songs = json.loads(string_js)
    number_of_rec=500
    song_list={}
    count = 0
    while len(song_list) < number_of_rec:
        if track_exists(playlist_tracks, popular_songs["songs"][count]['id']) == -1:
            song_list[str(count)] = popular_songs["songs"][count]['id']
            count+=1
        else:
            count += 1


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

    popularity = "song_popularity_sorted.json"
    challenge = "challenge_set.json"

    f = open(challenge)
    js = f.read()
    f.close()
    data = json.loads(js)
    start=0
    end=len(data['playlists'])
    result=open("random_recommendations_2.csv", "w")
    random_recommender_2(data, result, start, end)