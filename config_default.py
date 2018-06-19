#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Default configurations.
'''

__author__ = 'Michael Liao'

configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'Mysql2018',
        'db': 'PLC'
 
    },
    'session': {
        'secret': 'Awesome'
    },
    'PLCtype':{#各类型站台的配置
        },
    'prefixoflcd':{ #流程单前缀
        }
    
}
