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
        #creo una lista vacia, es necesario que sea un lista para guardar todos los stats de X como dataframe, 
        #para acceder a cada uno se debe usar la lista. Ejemplo: x.stat[0], x.stat[1], y castearla como dataframe.
        self.stat = []
        
        self.starttime = datetime.now()
        for i in range(self.n): 
            if self.x[self.vars[i]].size - sum(self.x[self.vars[i]].isnull()) > 0:
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
            else:
                Print(self.vars[i], 'es Nulo')
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
        stat['PD'] = stat['bad'] / stat['obs']
        
        stat['woe'] = np.log(stat['p_good'] / stat['p_bad'])

        iv_stat = (stat['p_good'] - stat['p_bad'])* stat['woe']
        iv = iv_stat.replace([np.inf, -np.inf], np.nan).dropna().sum()
        
        return iv, stat, t_obs
    
    def _estimatedtime(self, starttime, endtime, n):
        print('Se estima que acabará a las: ', str(starttime+(endtime-starttime)*n), '\n')
        
    def _getLabels(self, x, breaks):
        if isinstance((breaks),list):
            _breaks = breaks
        elif x.dtype.name != 'object' and x.dtype.name != 'category':
            _breaks = np.unique(np.percentile(x[np.logical_not(x.isnull().values)], np.arange(breaks+1)*100/breaks))
        if x.dtype.name != 'object' and x.dtype.name != 'category':
            if _breaks.size > 1:
                labels = pd.cut(x, bins = _breaks, include_lowest=True)
            else:
                labels = x
        elif x.dtype.name != 'category':
            labels = x.copy()
        else:
            labels = x.astype('category')
        return (labels)
    
    def top(self, n=np.nan, ivmin=np.nan, ivmax=np.nan, part='names'):
        if np.isnan(n) and np.isnan(ivmin) and np.isnan(ivmax ):
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
        
    def plot(self, x, season = np.nan, breaks = None):
        if breaks is None:
            _x = self.x[x]
        else:
            _x = self._getLabels(self.x[x], breaks)
    
        df = pd.DataFrame({'X':_x, 'Y':self.y})
        p = df.groupby('X')['Y'].agg([np.size, np.sum]).rename(columns = {'size':'Total', 'sum':'Bad'})
        p['R'] = p['Bad'] / p['Total']
        if np.isnan(season):
            p['R'].plot()
        else:
            p['R'].plot().xaxis.set_ticks(np.arange(np.min(self.x[x]), np.max(self.x[x]), season))
        return
    def copy(self):
        print(self.iv)
        self.stat[0].to_clipboard()
