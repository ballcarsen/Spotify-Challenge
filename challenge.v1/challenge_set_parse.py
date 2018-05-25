#challenge 1: [0:1000]
#challenge 2: [9000:10000]
#challenge 3: [1000:2000]
#challenge 4: [2000:3000]
#challenge 5: [3000:4000]
#challenge 6: [4000:5000]
#challenge 7: [5000:6000]
#challenge 8: [6000:7000]
#challenge 9: [7000:8000]
#challenge 10: [8000:9000]
import json

file_name = "challenge_set.json"


with open(file_name, 'r') as file:
    challenge_set = json.load(file)

slice = challenge_set['playlists'][8000:9000]

count = 1000
with open('challenge_10.json', 'w') as f:
    f.write("{ \"songs\": \n")
    json.dump(slice, f, indent=2)
    f.write("}")