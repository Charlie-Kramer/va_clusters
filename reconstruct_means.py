#after ISYE6740 HW3-see notes
#need to add back mean of original data (gamma)
def mapback(mu,U_k,lambda_k):
    '''
    given:
      mu        KxM matrix of means (row j is mean of jth distribution)
      U_k       NxK matrix of eigenvectors (N features in original dataset, K in reduced)
      lambda_k  KxK diagonal matrix of singular values (sqrt of eigenvalues)

    return:
      mu_hat NxM matrix of reconstructed mean features
    '''

    mu_hat = np.matmul(np.matmul(np.transpose(U_k),lambda_k),np.transpose(mu))
    print("mu hat", mu_hat)
    print("mu hat shape", mu_hat.shape)

    return mu_hat
