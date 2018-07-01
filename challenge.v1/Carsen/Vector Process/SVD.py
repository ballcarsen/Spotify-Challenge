#import sklearn.cluster.Kmeans as kmeans
from sklearn.decomposition import TruncatedSVD
import pandas as pd
import numpy as np

def create_transformer(arr):

    transformer = TruncatedSVD(n_components=100)

    out = transformer.fit_transform(arr)

    print('Trained Transformer')
    print(str(transformer.explained_variance_ratio_) + " explained variance")
    print(str(transformer.explained_variance_ratio_.sum()) + " explained variance ratio sum")
    np.save('transformed_data', out)
    return(transformer)

def perform_transform(arr, transformer, outfile):
    transformed_array = transformer.transform(arr)

    return transformed_array



if __name__ == '__main__':

    tf = create_transformer(np.load('data_arr.npy'))

    print('Transformer Created')

    perform_transform(np.load('data_arr.npy'), tf, 'transformed_data')


    c_4 = np.load('challenge_vectors4.npy')
    c_5 = np.load('challenge_vectors5.npy')
    c_6 = np.load('challenge_vectors6.npy')
    c_7 = np.load('challenge_vectors7.npy')
    c_8 = np.load('challenge_vectors8.npy')
    c_9 = np.load('challenge_vectors9.npy')
    c_10 = np.load('challenge_vectors10.npy')

    challenge = perform_transform(c_4, tf, 'c_4_t')

    challenge = np.vstack((challenge, perform_transform(c_5, tf, 'c_5_t')))
    print('5 inserted')
    print(challenge.shape)

    challenge = np.vstack((challenge, perform_transform(c_6, tf, 'c_6_t')))
    print('6 inserted')

    challenge = np.vstack((challenge, perform_transform(c_7, tf, 'c_7_t')))
    print('7 inserted')

    challenge = np.vstack((challenge, perform_transform(c_8, tf, 'c_8_t')))
    print('8 inserted')

    challenge = np.vstack((challenge, perform_transform(c_9, tf, 'c_9_t')))
    print('9 inserted')

    challenge = np.vstack((challenge, perform_transform(c_10, tf, 'c_10_t')))
    print('10 inserted')

    np.save('transformed_challenge', challenge)


