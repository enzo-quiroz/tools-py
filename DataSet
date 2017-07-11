import numpy as np

class DataSet(object):
    def __init__(self,
                 x,
                 y,
                 seed):
        np.random.seed(1 if seed is None else seed)
        
        self._cases = x.shape[0]
        self._x = x
        self._y = y
        self._epochs_completed = 0
        self._index_in_epoch = 0
    
    def next_batch(self, batch_size):
        start = self._index_in_epoch
        if start == 0 and self._epochs_completed ==0:
            perm0 = np.arange(self._cases)
            np.random.shuffle(perm0)
            
            self._x = self._x[perm0]
            self._y = self._y[perm0]
