import pandas as pd
import numpy as np
from datetime import datetime 

__author__ = 'Enzo Quiroz'

class WoE:
    def __init__(self, data, x, y, breaks=None, echo=False, echo_type='none'):
        # x: debe ser una lista, ejem: x=[col1, col2, col3], x=[col1]
        
        self.vars = x
        self.x = data[x].copy()
        self.y = data[y].copy()
        self.breaks = breaks
        self.iv = pd.DataFrame()
        self.n = len(x)
        #creo una lista vacia
        self.stat = []
        
        self.starttime = datetime.now()
        for i in range(self.n): 
            _iv, _stat = self.woe(x = self.x[self.vars[i]], y = self.y, breaks = self.breaks)
            if not np.isnan(_iv):
                self.iv = self.iv.append({'Variable': self.vars[i], 'IV': _iv}, ignore_index=True)[['Variable','IV']]
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
        if df['X'].dtype.name != 'object':
            df['labels'] = pd.cut(df['X'], bins = breaks)
        else:
            df['labels']= df['X'].astype('category')
        col_names = {'count_nonzero':'bad', 'size':'obs'}
        stat = df.groupby('labels')['Y'].agg([np.count_nonzero, np.size]).rename(columns = col_names).copy()
        stat['good'] = stat['obs'] - stat['bad']
        t_good = stat['good'].sum()
        t_bad = stat['bad'].sum()
        t_obs = stat['obs'].sum()

        stat['p_good'] = stat['good'] / t_good
        stat['p_bad'] = stat['bad'] / t_bad
        stat['p_obs'] = stat['obs'] / t_obs
        stat['PD'] = stat['bad'] / t_obs
        
        stat['woe'] = np.log(stat['p_good'] / stat['p_bad'])

        iv_stat = (stat['p_good'] - stat['p_bad'])* stat['woe']
        iv = iv_stat.replace([np.inf, -np.inf], np.nan).dropna().sum()
        
        return iv, stat
    
    def _estimatedtime(self, starttime, endtime, n):
        print('Se estima que acabará a las: ', str(starttime+(endtime-starttime)*n), '\n')
        
    #Aun no implementado del todo, verificar si pd.cut genera ya los percentiles
    def _getLabels(self, x, breaks):
        if type(breaks) == 'list':
            _breaks=breaks
        else:
            np.percentile(x, )
        if x.dtype.name != 'object':
            df['labels'] = pd.cut(df['X'], bins = _breaks)
        else:
            df['labels']= df['X'].astype('category')
            
