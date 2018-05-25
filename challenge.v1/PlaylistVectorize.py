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
from PreprocessingFunctions import get_vector_of_playlist

client = MongoClient('localhost', 27017)
db = client['spotify-challenge']
artist = db['artists-collection']

length = artist.count()
vectors  = open('challenge_4_vectors.csv', "a")

db.drop_collection(artist)
createMongoDB_artistCollection()






