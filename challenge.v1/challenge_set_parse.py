import json

file_name = "challenge_set.json"
challenge_1_count = 0
challenge_2_count = 0
challenge_3_count = 0
challenge_4_count = 0
challenge_5_count = 0
challenge_6_count = 0
challenge_7_count = 0
challenge_8_count = 0
challenge_9_count = 0
challenge_10_count = 0

with open(file_name, 'r') as file:
    challenge_set = json.load(file)
'''
count = 8000
while count < 9000:
        print(challenge_set["playlists"][count]["name"],challenge_set["playlists"][count]["num_tracks"],challenge_set["playlists"][count]["num_samples"])
        count += 1
'''
slice = challenge_set['playlists'][1000:2000]

count = 1000
with open('challenge_3.json', 'w') as f:
    json.dump(slice, f, indent=2)