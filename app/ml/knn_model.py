import numpy as np
from collections import Counter

# KNN Classifier Implementation

class KNNModel:
    def __init__(self, k=3):
        self.k = k
        
    def fit(self, X, y):
        self.X_train = X
        self.y_train = y
    
    def predict(self, X):
        predictions = [self._predict(x) for x in X]
        return np.array(predictions)
    
    def _predict(self, x):
        # Compute distances between x and all examples in the training set
        distances = [np.sqrt(np.sum((x - x_val) ** 2)) for x_val in self.X_train]
        
        # Sort by distance and return indices of the first k neighbors
        k_indices = np.argsort(distances)[:self.k]
        
        # Extract the labels of the k nearest neighbors
        k_nearest_labels = [self.y_train[i] for i in k_indices]
        
        # Return the most common class label
        most_common = Counter(k_nearest_labels).most_common(1)
        return most_common[0][0]


def windowed_statistics(X, window_size):
    X_windows = []
    for i in range(0, len(X), window_size):
        X_win = X[i:i+window_size]
        if len(X_win) == window_size:
            mean = np.mean(X_win, axis=0)
            std = np.std(X_win, axis=0)
            X_windows.append(np.concatenate([mean, std]))
    return np.array(X_windows)