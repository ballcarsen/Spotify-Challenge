# coding=utf-8
import json
import sys

reload(sys)
sys.setdefaultencoding('utf8')

artists = ['Drake','Kanye West','Kendrick Lamar','Rihanna','The Weeknd','Eminem','Ed Sheeran','Future','Justin Bieber','J. Cole','Beyoncé','The Chainsmokers','Chris Brown', 'Calvin Harris','Twenty One Pilots','Lil Uzi Vert','Post Malone','Big Sean','Maroon 5','JAY Z']
f = open("Drake.json", "w")
f.write("{ \"songs\": [\n")
f1 = open("Kanye West.json", "w")
f1.write("{ \"songs\": [\n")
f2 = open("Kendrick Lamar.json", "w")
f2.write("{ \"songs\": [\n")
f3 = open("Rihanna.json", "w")
f3.write("{ \"songs\": [\n")
f4 = open("The Weeknd.json", "w")
f4.write("{ \"songs\": [\n")
f5 = open("Eminem.json", "w")
f5.write("{ \"songs\": [\n")
f6 = open("Ed Sheeran.json", "w")
f6.write("{ \"songs\": [\n")
f7 = open("Future.json", "w")
f7.write("{ \"songs\": [\n")
f8 = open("Justin Bieber.json", "w")
f8.write("{ \"songs\": [\n")
f9 = open("J. Cole.json", "w")
f9.write("{ \"songs\": [\n")
f10 = open("Beyoncé.json", "w")
f10.write("{ \"songs\": [\n")
f11 = open("The Chainsmokers.json", "w")
f11.write("{ \"songs\": [\n")
f12 = open("Chris Brown.json", "w")
f12.write("{ \"songs\": [\n")
f13 = open("Calvin Harris.json", "w")
f13.write("{ \"songs\": [\n")
f14 = open("Twenty One Pilots.json", "w")
f14.write("{ \"songs\": [\n")
f15 = open("Lil Uzi Vert.json", "w")
f15.write("{ \"songs\": [\n")
f16 = open("Post Malone.json", "w")
f16.write("{ \"songs\": [\n")
f17 = open("Big Sean.json", "w")
f17.write("{ \"songs\": [\n")
f18 = open("Maroon 5.json", "w")
f18.write("{ \"songs\": [\n")
f19 = open("JAY Z.json", "w")
f19.write("{ \"songs\": [\n")

if __name__ == '__main__':
    f_popular_songs = open("song_popularity_sorted.json", "r")
    string_js = f_popular_songs.read()
    f_popular_songs.close()
    popular_songs = json.loads(string_js)
    song_list = []
    for song in popular_songs["songs"]:
        if song["artist"] in artists:
            song_list.append(song)
    for song in song_list:
        if song["artist"] in artists[0]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f.write(line)
    for song in song_list:
        if song["artist"] in artists[1]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f1.write(line)
    for song in song_list:
        if song["artist"] in artists[2]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f2.write(line)
    for song in song_list:
        if song["artist"] in artists[3]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f3.write(line)
    for song in song_list:
        if song["artist"] in artists[4]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f4.write(line)
    for song in song_list:
        if song["artist"] in artists[5]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f5.write(line)
    for song in song_list:
        if song["artist"] in artists[6]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f6.write(line)
    for song in song_list:
        if song["artist"] in artists[7]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f7.write(line)
    for song in song_list:
        if song["artist"] in artists[8]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f8.write(line)
    for song in song_list:
        if song["artist"] in artists[9]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f9.write(line)
    for song in song_list:
        if song["artist"] in artists[10]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f10.write(line)
    for song in song_list:
        if song["artist"] in artists[11]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f11.write(line)
    for song in song_list:
        if song["artist"] in artists[12]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f12.write(line)
    for song in song_list:
        if song["artist"] in artists[13]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f13.write(line)
    for song in song_list:
        if song["artist"] in artists[14]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f14.write(line)
    for song in song_list:
        if song["artist"] in artists[15]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f15.write(line)
    for song in song_list:
        if song["artist"] in artists[16]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f16.write(line)
    for song in song_list:
        if song["artist"] in artists[17]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f17.write(line)
    for song in song_list:
        if song["artist"] in artists[18]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f18.write(line)
    for song in song_list:
        if song["artist"] in artists[19]:
            line = "\t\t" + json.dumps(song) + "," + '\n'
            f19.write(line)

    f.write("] \n }")
    f1.write("] \n }")
    f2.write("] \n }")
    f3.write("] \n }")
    f4.write("] \n }")
    f5.write("] \n }")
    f6.write("] \n }")
    f7.write("] \n }")
    f8.write("] \n }")
    f9.write("] \n }")
    f10.write("] \n }")
    f11.write("] \n }")
    f12.write("] \n }")
    f13.write("] \n }")
    f14.write("] \n }")
    f15.write("] \n }")
    f16.write("] \n }")
    f17.write("] \n }")
    f18.write("] \n }")
    f19.write("] \n }")


    f.close()
    f2.close()
    f3.close()
    f4.close()
    f5.close()
    f6.close()
    f7.close()
    f8.close()
    f9.close()
    f10.close()
    f11.close()
    f12.close()
    f13.close()
    f14.close()
    f15.close()
    f16.close()
    f17.close()
    f18.close()
    f19.close()




    print("FINISHED");
