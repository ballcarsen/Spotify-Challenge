from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

data = np.load('transformed_data.npy')
labels = np.load('data_labels.npy')

challenge_data = np.load('transformed_challenge.npy')
challenge_labels = np.load('challenge_labels.npy')


print(challenge_data.shape)
print(challenge_labels.shape)

num_clusters = 75

data_dict = dict.fromkeys(range(num_clusters))


kmeans = KMeans(n_clusters= num_clusters, max_iter=10000,  random_state= 1).fit(data)
c_4_predict = kmeans.predict(challenge_data)


for i in range(num_clusters):
    data_dict[i] = {}
    data_dict[i]['data set playlists'] = []
    data_dict[i]['challenge set playlists'] = []
    data_dict[i]['centroid'] = []
centroids = kmeans.cluster_centers_

for i in range(len(centroids)):
    for point in centroids[i]:
        data_dict[i]['centroid'].append(point)

for point in range(len(kmeans.labels_)):
    data_dict[kmeans.labels_[point]]['data set playlists'].append(int(labels[point]))


for point in range(len(c_4_predict)):
    data_dict[kmeans.labels_[point]]['challenge set playlists'].append(int(challenge_labels[point]))

def visualize():
    x = []
    y = []
    cluster = []
    c = np.random.rand(num_clusters)
    colors = iter(cm.rainbow(np.linspace(0, 1, num_clusters)))
    for i in range(num_clusters):
        playlists = data_dict[i]['data set playlists']
        for playlist in playlists:
            index = np.where(labels == playlist)[0]
            x.append(data[index][0][0])
            y.append(data[index][0][1])
            cluster.append(i)

    for x, y in x,y:
        plt.scatter(x,y, c=next(colors), s=2)
    plt.show()
def hist(data):
    plt.hist(data, bins = 70)
    plt.title("Histogram of Cluster Sizes")
    plt.show()
#visualize()
min_d = 1000000
min_c = 1000000
max_d = 0
max_c = 0
data_cluster_sizes = []
challenge_cluster_sizes = []
with open('cluster_results_final.json', 'w') as out:
    out.write("{ \"Clusters\" :\n\t[\n")

    for i in range(num_clusters):
        print("challenge set")
        length = len(np.unique(data_dict[i]['challenge set playlists']))
        challenge_cluster_sizes.append(length)
        if min_c > length:
            min_c = length
        if max_c < length:
            max_c = length
        print(len(np.unique(data_dict[i]['challenge set playlists'])))
        print(len(data_dict[i]['challenge set playlists']))

        print('data set')
        length = len(np.unique(data_dict[i]['data set playlists']))
        data_cluster_sizes.append(length)
        if min_d > length:
            min_d = length
        if max_d < length:
            max_d = length
        print(len(np.unique(data_dict[i]['data set playlists'])))
        print(len(data_dict[i]['data set playlists']))

        out.write('\t\t{\n')
        out.write('\t\t\t\"Cluster\" : ' + str(i) + ',\n')
        out.write('\t\t\t\"data set playlists\" : ' + str(data_dict[i]['data set playlists']) + ",\n")
        out.write('\t\t\t\"challenge set playlists\" : ' + str(data_dict[i]['challenge set playlists']) + ',\n')
        out.write('\t\t\t\"centroid\" : ' + str(data_dict[i]['centroid']) + '\n')


        if i < num_clusters - 1:
            out.write('\t\t},\n')
        else :
            out.write('\t\t}\n')
    out.write("\t]\n}")
    print(str(min_d) + " " +  str(max_d) + " " + str(min_c) + " " + str(max_c))
out.close()
print(np.average(data_cluster_sizes))
hist(data_cluster_sizes)
