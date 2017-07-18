from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np

class DataSet(object):
    def __init__(self, x, y, seed = None, factores = None):
        np.random.seed(1 if seed is None else seed)
        self._cases = x.shape[0]
        self._x = self.encode(x)
        if factores == None:
            self._y = self.encode(y)
        else:
            self._y = self.factor_a_matriz(self.encode(y), factores)
        self._epochs_completed = 0
        self._index_in_epoch = 0
        
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    def encode(self, data):
        if isinstance(data, pd.Series) :
            if data.dtypes == 'object' :
                le = LabelEncoder()
                data = le.fit_transform(data)
            else:
                data = data.values
            return data
        else :
            var_to_mod = data.columns[data.dtypes == 'object']
            if var_to_mod.size > 0 :
                le = LabelEncoder()
                for i in var_to_mod:
                    data[i] = le.fit_transform(data[i])
            if isinstance(data, pd.DataFrame):
                return data.values
            else:
                return data
    
    def decode(self, data):
        #To do
        return None
    
    def factor_a_matriz(self, df, factores):
            df_ = df
            if isinstance(df, pd.Series):
                df_ = df.values
            if df_.shape[0] == df_.size:
                casos = df_.shape[0]
                indices = np.arange(casos) * factores 
                factores_uno = np.zeros((casos, factores))
                factores_uno.flat[indices + df_.ravel()] = 1 #En cada factor mas el único valor de la etiqueta coloca un 1
                return factores_uno
            else:
                return df_
    
    def next_batch(self, batch_size, random = True):
        start = self._index_in_epoch
        if start == 0 and self._epochs_completed == 0 and random:
            perm0 = np.arange(self._cases)
            np.random.shuffle(perm0)
            
            self._x = self._x[perm0]
            self._y = self._y[perm0]
            
        if start + batch_size > self._cases:
            self._epochs_completed +=1
            rest_num = self._cases - start
            x_rest = self._x[start:self._cases]
            y_rest = self._y[start:self._cases]
            
            if random:
                perm = np.arange(self._cases)
                np.random.shuffle(perm)
                
                self._x = self._x[perm]
                self._y = self._y[perm]
            start = 0
            self._index_in_epoch = batch_size - rest_num
            end = self._index_in_epoch
            x_new_part = self._x[start:end]
            y_new_part = self._y[start:end]
            
            return np.concatenate((x_rest, x_new_part), axis = 0), np.concatenate((y_rest, y_new_part), axis = 0)
        else:
             self._index_in_epoch += batch_size
             end = self._index_in_epoch
             return self._x[start:end], self._y[start:end]
