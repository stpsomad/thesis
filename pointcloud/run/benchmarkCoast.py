# -*- coding: utf-8 -*-
"""
Created on Mon Apr 04 14:38:34 2016

@author: Stella Psomadaki
"""

from pointcloud.AbstractBulkLoader import BulkLoader
from pointcloud.AbstractQuerier import Querier
import time
from tabulate import tabulate
import pointcloud.oracleTools as ora


benchmark = ['mini', 'medium', 'full']  
hloading = ['approach', 'preparation', 'loading', 'closing', 'size[MB]', 'points']

integrations = ['lxyt']
scalings = ['1']


for integr in integrations:
    for scaling in scalings:
        loadings = []
        queries = []
        for i in range(1,4):
            configuration = 'D:/Dropbox/Thesis/Thesis/Code/ini/coastline/{0}_{1}_part{2}.ini'.format(integr, scaling, i)
            bulk = BulkLoader(configuration)
            loading = []
            loading.append(benchmark[i - 1])
                      
            start = time.time()
            bulk.preparation()
            loading.append(round(time.time() - start, 2))
            
            start = time.time()
            bulk.loading()
            loading.append(round(time.time() - start, 2))
            
            start = time.time()
            bulk.closing()
            loading.append(round(time.time() - start, 2))
           
            size, points = bulk.statistics()
            loading.append(round(size,2))
            loading.append(int(points))
            
            loadings.append(loading)
            print tabulate(loadings, hloading, tablefmt="plain")
            
    
    print 'writing to file statistics for case: {0}_{1}_{2}'.format(bulk.integration, bulk.parse, bulk.scale)
        f = open('loading_stats_31_03_load_2.txt', 'a')
        f.write('Statistics for case: {0} {1} {2}\n'.format(bulk.integration, bulk.parse, bulk.scale))
        f.write(tabulate(loadings, hloading, tablefmt="plain"))
        f.write('\n')