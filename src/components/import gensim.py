import gensim
import torch
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy as np
import time

def get_word_vectors(wordset, model):
    word_vectors = []
    valid_words = []
    invalid_words = []

    for word in wordset:
        if word in model:
            word_vectors.append(torch.tensor(model[word], dtype=torch.float32))
            valid_words.append(word)
        else:
            invalid_words.append(word)
    return torch.stack(word_vectors), valid_words, invalid_words

def dimension_reduction(vectors):
    word_vectors_numpy = vectors.cpu().detach().numpy()
    
    pca = PCA(n_components=2)
    ret = pca.fit_transform(word_vectors_numpy)
    return ret

def plot_embeddings(input_dict):
    fig, axs = plt.subplots(1, len(input_dict))
    for idx, key in enumerate(input_dict.keys()):
        vectors = input_dict[key]['vector']
        words = input_dict[key]['word']
        
        for i, word in enumerate(words):
            axs[idx].scatter(vectors[i,0], vectors[i,1], marker='*')
            axs[idx].text(vectors[i,0]+0.01, vectors[i,1]+0.01, word, fontsize=12)
            
        axs[idx].set_title(key)
    plt.show()
    plt.savefig('./results.png')
    print('Figure is saved...')
    return None

if __name__ == "__main__":
    model_load_cost_start = time.time()
    word2vec_model_path = 'GoogleNews-vectors-negative300.bin'
    word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(word2vec_model_path, binary=True)
    model_load_cost_end = time.time()
    print(f'Model load cost: {model_load_cost_end - model_load_cost_start:.2f} seconds')
    
    wordset = [
    'love', 'affection', 'passion', 'adoration', 'hate', 'dislike', 'loathe',

    'car', 'airplane', 'bicycle', 'train', 'fast', 'slow', 'vehicle', 'transportation',

    'dog', 'cat', 'cow', 'bird', 'bark', 'meow', 'moo', 'chirp',

    'USA', 'France', 'Japan', 'South Korea', 'Washington', 'Paris', 'Tokyo', 'Seoul',

    'morning', 'afternoon', 'evening', 'night'
    ]
    
    embedding_start_time = time.time()
    word_vectors, valid_words, invalid_words = get_word_vectors(wordset, word2vec_model)
    embedding_end_time = time.time()
    print(f'Embedding cost: {embedding_end_time - embedding_start_time:.2f} seconds')
    
    dimension_reduction_start_time = time.time()
    vector = dimension_reduction(word_vectors)
    return_dict = {}
    return_dict['PCA'] = {'vector': vector, 'word': valid_words, 'invalid_word': invalid_words}
    dimension_reduction_end_time = time.time()
    print(f'Dimension reduction cost: {dimension_reduction_end_time - dimension_reduction_start_time:.2f} seconds')
    
    plot_embeddings(return_dict)