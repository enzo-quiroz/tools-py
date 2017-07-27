import numpy as np
import math
import pandas as pd


class text_similarity(object):
    def __init__(self, w1, w2):
        self._w1 = w1,
        self._w2 = w2
        self.prob, self.prefijos, self.base, self.sufijos = self.probability(w1, w2)

    
    def text_to_number(self, text):
        text_number = np.zeros(len(text))
        for i in range(text_number.shape[0]):
                text_number[i] = ord(text[i])-96
        return text_number
    
    def number_to_text(self, number):
        _number = number.astype(int)
        number_text = ''
        for i in range(_number.shape[0]):
            if _number[i] > 0:
                number_text += chr(_number[i]+96)
        return number_text
    
    def get_best_primitive(self, primitive):    
        _primitive = primitive[0]
        results = pd.DataFrame(columns = ['Inicio','Fin','Largo'])
        _inicio = 0
        for i in range(_primitive.shape[0]):
             if i > 0:
                 if _primitive[i]-a > 1:
                   _fin = i-1
                   result_ = pd.DataFrame({'Inicio':[_inicio], 'Fin':[_fin], 'Largo':[_fin - _inicio]}, index = None)
                   results = results.append(result_)
                   _inicio = i
             a = _primitive[i]
        _fin = _primitive.shape[0]
        result_ = pd.DataFrame({'Inicio':[_inicio],'Fin':[_fin],'Largo':[_fin-_inicio]}, index = None)
        results = results.append(result_)
        results = results.reset_index(drop=True)
        results = results.loc[results['Largo']==results['Largo'].max()][0:].copy()
        return (_primitive[results['Inicio'].values[0]:results['Fin'].values[0]])

    def probability(self, w1, w2):
        if len(w1)>0 and len(w2)>0:
            if len(w1) <= len(w2):
                _w1 = w1
                _w2 = w2
            else:
                _w1 = w2
                _w2 = w1
            _lw1 = len(_w1)
            _lw2 = len(_w2)
            matrix_number = np.zeros([1, _lw2])
            matrix_number = np.vstack([matrix_number, self.text_to_number(_w2)])
            _w1_tn = self.text_to_number(_w1)
            for i in range(_lw1):
                matrix_number[0,i]=_w1_tn[i]
            
            test_matrix = np.zeros([_lw1 + _lw2, _lw1 + 2*_lw2 - 2])
            for i in range(_lw1):
                test_matrix[0,i+_lw2-1] = matrix_number[0][i]   
            for i in range(_lw2):
                for j in range(_lw1 + _lw2 - 1):
                    test_matrix[j+1,i+j] = matrix_number[1][i]
            square = np.nan
            primitive = np.nan
            pos = 0
            v1 = test_matrix[:][0]
            for i in range(_lw1 + _lw2 - 1):
                v2=test_matrix[:][i+1]
                _square = np.count_nonzero(v1-v2==0)
        
                if not(square > _square):
                    pos=i+1
                    equals = np.count_nonzero((v1-v2==0) & ~(v1==0) & ~(v2==0))
                    primitive = self.get_best_primitive(np.nonzero((v1-v2==0) & ~(v1==0) & ~(v2==0)))
                    square=_square
            base=''
            if equals > 0:         
                prefijo1 = self.number_to_text(test_matrix[:][0][0:primitive[0]])
                prefijo2 = self.number_to_text(test_matrix[:][pos][0:primitive[0]])
                base = self.number_to_text(test_matrix[:][0][primitive[0]:primitive[primitive.shape[0]-1]+1])
                sufijo1 = self.number_to_text(test_matrix[:][0][primitive[primitive.shape[0]-1]+1:])
                sufijo2 = self.number_to_text(test_matrix[:][pos][primitive[primitive.shape[0]-1]+1:])
            
    #        print("p1: " + prefijo1)
    #        print ("p2: " + prefijo2)
    #        print("Base: "+base)     
    #        print("p1: " + sufijo1)
    #        print ("p2: " + sufijo2) 
                if len(prefijo1) > 0 and len(prefijo2)>0:
                    prefijos = [prefijo1, prefijo2]
                elif len(prefijo1)>0:
                    prefijos = [prefijo1]
                elif len(prefijo2)>0:
                    prefijos = [prefijo2]
                else:
                    prefijos = None
                
                if len(sufijo1) > 0 and len(sufijo2)>0:
                    sufijos = [sufijo1, sufijo2]
                elif len(sufijo1)>0:
                    sufijos = [sufijo1]
                elif len(sufijo2)>0:
                    sufijos = [sufijo2]
                else:
                    sufijos = None
        else:
            base=''
            _lw1 = 1
            
        if len(base)<3 :
            equals = 0
            base = ''
            sufijos = None
            prefijos = None
        return equals / _lw1, prefijos, base, sufijos
