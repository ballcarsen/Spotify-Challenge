import json
import sys
from pymongo import MongoClient
import numpy as np
import csv


sys.path.append('/Users/Carsen/git/Spotify-Challenge/challenge.v1/Sheny')
sys.path.append('/Users/Carsen/git/Spotify-Challenge/challenge.v1/Sheny')

file = 'data/mpd.slice.0-999.json'

from PreprocessingFunctions import createMongoDB_artistCollection
from PreprocessingFunctions import get_index

client = MongoClient('localhost', 27017)
db = client['spotify-challenge']
artist = db['artists-collection']

length = artist.count()
vectors  = open('vectors.csv', "a")

#db.drop_collection(artist)
#createMongoDB_artistCollection()
count = 1
with open (file, 'r') as data:
    data = json.load(data)
    for playlist in data['playlists']:
        temp = np.zeros((length,) , dtype= int)
        vectors.write(str(playlist["pid"]) + ', ')
        for track in playlist['tracks']:
            index = get_index(track['artist_uri'])
            temp[index] += 1
        temp.astype(int)
        temp = []
        print("wrote new playlist")





