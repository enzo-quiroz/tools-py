import pandas as pd
import numpy as np
from datetime import datetime 

__author__ = 'Enzo Quiroz'

class WoE:
    def __init__(self, data, x, y, breaks=None, echo=False, echo_type='none', byzero = 0.001):
        # x: debe ser una lista, ejem: x=[col1, col2, col3], x=[col1]
        
        self.vars = x
        self.byzero = byzero
        self.x = data[x].copy()
        self.y = data[y].copy()
        self.breaks = breaks
        self.iv = pd.DataFrame()
        self.n = len(x)
        #creo una lista vacia
        self.stat = []
        
        self.starttime = datetime.now()
        for i in range(self.n): 
            _iv, _stat, _obs = self.woe(x = self.x[self.vars[i]], y = self.y, breaks = self.breaks)
            if not np.isnan(_iv):
                self.iv = self.iv.append({'Variable': self.vars[i], 'IV': _iv, 'Valid obs': _obs}, ignore_index=True)[['Variable','IV', 'Valid obs']]
                self.stat.append(_stat)
            if i==0:
                self._estimatedtime(self.starttime, datetime.now(), self.n)
            if echo:
                print(self.vars[i],': ', _iv)
            if echo_type == 'stat':
                print(_stat[['good','bad','obs','PD','woe']], '\n')
        self.iv = self.iv.sort_values('IV', ascending = False)
        self.endtime = datetime.now()
        print('Se ejecutó en: ', str(self.endtime-self.starttime))
    
    def woe(self, x, y, breaks):
        df = pd.DataFrame({"X": x, "Y": y, 'order': np.arange(x.size)})
        df['labels'] = self._getLabels(x, breaks)
        col_names = {'count_nonzero':'bad', 'size':'obs'}
        stat = df.groupby('labels')['Y'].agg([np.count_nonzero, np.size]).rename(columns = col_names).copy()
        stat['good'] = stat['obs'] - stat['bad']
        t_good = np.maximum(stat['good'].sum(), self.byzero)
        t_bad = np.maximum(stat['bad'].sum(), self.byzero)
        t_obs = stat['obs'].sum()

        stat['p_good'] = np.maximum(stat['good'] / t_good, self.byzero)
        stat['p_bad'] = np.maximum(stat['bad'] / t_bad, self.byzero)
        stat['p_obs'] = stat['obs'] / t_obs
        stat['PD'] = stat['bad'] / t_obs
        
        stat['woe'] = np.log(stat['p_good'] / stat['p_bad'])

        iv_stat = (stat['p_good'] - stat['p_bad'])* stat['woe']
        iv = iv_stat.replace([np.inf, -np.inf], np.nan).dropna().sum()
        
        return iv, stat, t_obs
    
    def _estimatedtime(self, starttime, endtime, n):
        print('Se estima que acabará a las: ', str(starttime+(endtime-starttime)*n), '\n')
        
    #Aun no implementado del todo, verificar si pd.cut genera ya los percentiles
    def _getLabels(self, x, breaks):
        if type(breaks) == 'list':
            _breaks = breaks
        elif x.dtype.name != 'object':
            _breaks = np.unique(np.percentile(x[np.logical_not(x.isnull().values)], np.arange(breaks+1)*100/breaks))
        if x.dtype.name != 'object':
            labels = pd.cut(x, bins = _breaks)
        else:
            labels = x.astype('category')
        return (labels)
    
    def top(self, n=np.nan, ivmin=np.nan, ivmax=np.nan, part='names'):
        if np.isnan(n) and np.isnan(ivmin) and np.isnan(ivmax ):
            print('aji')
            raise ValueError("No se ha escogido criterio de seleción. Especificar alguno de los parámetros n, ivmin o ivmax")
        _n = n
        if n>self.n:
            _n = self.n
        if np.isnan(_n):
            _n = self.n
        if part == 'names':
            if np.isnan(ivmin) and np.isnan(ivmax ):
                return self.iv[0:_n]['Variable'].tolist()
            else:
                return self.iv.loc[np.logical_and(
                        (np.isnan(ivmin) or self.iv['IV']>=ivmin),
                        (np.isnan(ivmax) or self.iv['IV']<=ivmax))
                        ][0:_n]['Variable'].tolist()
        else:
            return 0
