#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
Settings for the automatic course registration robot for Fudan University Undergraduates.
'''
settings  = {'USER': None,
            'PSW': None,
            'LIST': ['CHIN119003.01',
                     'PHIL119001.01',
                     'HIST119007.01'
                     ],   # the courses you want
            'MAX_ATTEMPTS': 1000,    # try how many times before stop
            'PRINT_LOG': True,	# whether print log
            'INTERVAL' :1}		# interval between two attempts





