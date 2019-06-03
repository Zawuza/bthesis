import numpy as np

feature_count = 1
learning_rate = 0.01

def stochastic_gradient(matrix):
    m, n = matrix.shape
    voter_matrix = np.random.rand(m,feature_count)
    alternative_matrix = np.random.rand(feature_count, n)
    for _ in range(m*n*1000):
        i = np.random.randint(m)
        j = np.random.randint(n)
        if np.isnan(matrix[i][j]):
            continue
        approximate = 0
        for k in range(feature_count):
            approximate += voter_matrix[i][k] * alternative_matrix[k][j]
        error = matrix[i][j] - approximate
        for k in range(feature_count):
            voter_matrix[i][k] = voter_matrix[i][k] + 2*learning_rate*alternative_matrix[k][j]*error
            alternative_matrix[k][j] = alternative_matrix[k][j] + 2*learning_rate*voter_matrix[i][k]*error
        
    return voter_matrix, alternative_matrix

matrix = np.asarray([[2, 1, 0],[0, 2, 1],[np.nan, 0, 1]])
voters_features, alternatives_features = stochastic_gradient(matrix)
print(voters_features)
print(alternatives_features)
print(np.dot(voters_features,alternatives_features))