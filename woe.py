import pandas as pd
import numpy as np

__author__ = 'Enzo Quiroz'



class WoE:
    def __init__(self, data, x, y, breaks=None):
        self.vars = x
        self.x = data[x].copy()
        self.y = data[y].copy()
        self.breaks = breaks
        self.n = 1
        self.iv = pd.DataFrame()
        self.n = len(x)
        for i in range(self.n):
            print(i)
            #self.iv = self.iv.append(
            woe(self = self, x = self.x[self.vars[i]], y = self.y, breaks = self.breaks)
            #woe(self=self, x = self.x, y = self.y, breaks = self.breaks)
    
    def woe(self, x, y, breaks):
        df = pd.DataFrame({"X": x, "Y": y, 'order': np.arange(x.size)})
        df['labels'] = pd.cut(df['X'], bins = breaks)
        
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
        
        stat['woe'] = np.log(stat['p_good'] / stat['p_bad'])*100

        iv_stat = (stat['p_good'] - stat['p_bad'])* stat['woe']/100
        stat = stat
        iv = iv_stat.replace([np.inf, -np.inf], np.nan).dropna().sum()
        
        return iv
