from operator import itemgetter

import numpy as np
import codecs
import json
playlist_data = np.load('../Sheny/playlist_data.npy').item()
with open ('../song_popularity_sorted.json') as pop:
    song_pop = json.load(pop)
pop.close()


def song_test():
    for i in song_pop['songs']:
        print(i['id'])

def load_data(cp, clusp, cvp, clp, dvp, dlp, rp, rlp, challenge_path):
    with open(cp, 'r') as cha:
        cha_dict = json.load(cha)
    cha.close()

    with open(clusp, 'r') as cluster:
        cluster_dict = json.load(cluster)
    cluster.close()

    with open(challenge_path, 'r') as challenge_set:
        challenge_dict = json.load(challenge_set)
    challenge_set.close

    challenge_v = np.load(cvp)
    challenge_l = np.load(clp)
    data_v = np.load(dvp)
    data_l = np.load(dlp)
    recommended = np.load(rp)
    recommended_labels = np.load(rlp)

    return cha_dict, cluster_dict, challenge_v, challenge_l, data_v, data_l, recommended, recommended_labels, challenge_dict

def order_data_playlists(challenge_vect, cluster_data_vect, play_in_cluster_ids):
    distances = []
    for data in cluster_data_vect:
        dist = np.linalg.norm(challenge_vect - data)
        distances.append(dist)
    distances = np.array(distances)

    closest_vectors = []
    while(len(distances) != 0):
        min_loc = np.where(distances == distances.min())
        closest_vectors.append(play_in_cluster_ids[min_loc[0][0]])
        distances = np.delete(distances, min_loc[0][0])
        play_in_cluster_ids = np.delete(play_in_cluster_ids, min_loc[0][0])
    return closest_vectors

def order_songs(pid, data_songs):
    pass

def rec_for_one(pid, challenge_vec, data_in_cluster_ids, cluster_data_vect, rec, rec_l, challenge_dict):
    #playlist id's ordered in by the closest to the challenge vector
    rec_l = rec_l.astype(dtype= int)
    min_order = order_data_playlists(challenge_vec, cluster_data_vect, data_in_cluster_ids)
    rec_songs = []
    songs_in_challenge = []
    for playlist in challenge_dict['playlists']:
        if playlist['pid'] == pid:
            temp = playlist['tracks']
            for i in temp:
                songs_in_challenge.append(i['track_uri'])

    for id in min_order:
        if len(rec_songs) < 500:
            playlist = playlist_data[id]

            data_tracks = sorted(playlist['tracks'], key=itemgetter('frequency'), reverse=True)

            for i in data_tracks:
                if i['track_uri'] not in songs_in_challenge and i['track_uri'] not in rec_songs and len(rec_songs) < 500:
                    rec_songs.append(i['track_uri'])
        else:
            break

    if len(rec_songs) < 500:
        more_recommends = rec[np.where(rec_l == pid)[0][0]]
        print('not enough recomends')
        print(len(rec_songs))
        for extra in more_recommends:
            if extra not in rec_songs and len(rec_songs) < 500:
                rec_songs.append(extra)
            elif len(rec_songs) == 500:
                break
    if len(rec_songs) < 500:
        for i in song_pop['songs']:
            if i['id'] not in rec_songs and len(rec_songs) < 500:
                rec_songs.append(i['id'])
            elif len(rec_songs) == 500:
                break
    return rec_songs


def rec_for_cluster(cluster, challenge_v, challenge_l, data_v, data_l, rec, rec_l, challenge_dict, clus_num):
    data_in_cluster_ids = np.array(cluster['data set playlists'])

    #vectors of the data set playlists in the cluster
    data_vect = []
    #TODO catch the potential errors, empty clusters, empty data sets

    #get all the vectors of the data set playlists in the cluster
    for data_playlist in data_in_cluster_ids:
        loc = np.where(data_l == data_playlist)
        data_vect.append(data_v[loc[0][0]])

    with open('final_rec.csv', 'a') as out:
        count = 0
        print(len(np.unique(cluster['challenge set playlists'])))
        print(cluster['challenge set playlists'])
        print(len(cluster['challenge set playlists']))
        for challenge_playslist_id in cluster['challenge set playlists']:

            challenge_loc = np.where(challenge_l == challenge_playslist_id)[0][0]
            one_challenge_vec = challenge_v[challenge_loc]
            songs = rec_for_one(challenge_playslist_id, one_challenge_vec, data_in_cluster_ids, data_vect, rec, rec_l, challenge_dict)
            count += 1
            print("playlist done " + str(count) + " out of " + str(len(cluster['challenge set playlists'])) + " Cluster Number " + str(clus_num))

            out.write(str(challenge_playslist_id) + ',')
            if len(songs) != 500:
                print("Yah fucked up")
            for i in range(len(songs)):
                if i < len(songs) - 1:
                    out.write(songs[i] + ",")
            else:
                out.write(songs[i] + "\n")
    out.close
if __name__ == '__main__':

    data_path = 'challenge.v1/data'
    challenge_path = '../Challenge Set/challenge_set.json'
    challenge_vectors_path = 'all_c_vect.npy'
    challenge_labels_path = 'all_c_lab.npy'
    data_vectors_path = 'transformed_data.npy'
    data_labels_path = 'labels_arr_data.npy'
    cluster_path = 'cluster_results_final.json'
    random_rec = '../random_recommendations_2.csv'
    rp = 'recommended.npy'
    rlp = 'recommended_labels.npy'

    cha_dict, cluster_dict, challenge_v, challenge_l, data_v, data_l, rec, rec_l, challenge_dict = load_data(challenge_path, cluster_path,
                                                                         challenge_vectors_path, challenge_labels_path,
                                                                            data_vectors_path, data_labels_path, rp, rlp,
                                                                                                      challenge_path)
    #cluster = cluster_dict['Clusters'][41]
    #rec_for_cluster(cluster, challenge_v, challenge_l, data_v, data_l, rec, rec_l, challenge_dict, 41)


    for i in range(75):
        print('On cluster ' + str(i))
        cluster = cluster_dict['Clusters'][i]
        rec_for_cluster(cluster, challenge_v, challenge_l, data_v, data_l, rec, rec_l, challenge_dict, i)
    print('fucking done boiiiii')

