

def getCommonElements(title, BoW):
    return len(set(title).intersection(BoW))

def getTitlesWordsNo(t, b):
    return len(set(t).union(b))

if __name__ == '__main__':
    title = ['run', 'rihanna','rock', 'metal']
    BoW = ['rihanna', 'metal', 'trash', 'rock','something', 'bla']
    D1 = getCommonElements(title, BoW)
    D2 = getTitlesWordsNo(title, BoW)
    D = D1/float(D2)
    print ("{0:.2f}".format(D))