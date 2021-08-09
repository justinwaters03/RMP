# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 22:35:26 2021

@author: gcz5chn
"""
import os
os.chdir("..\..")
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp



#get data from returns_data.xlsx into dictionary
returns_dict = dm.get_equity_hedge_returns(all_data=True)

#create dictionary that contains updated returns
new_data_dict = dm.create_update_dict()

# #remove first n rows from daily dataframe
# n = 64
# new_data_dict['Daily'] = new_data_dict['Daily'].iloc[n:,]

# #remove first n rows from weekly dataframe
# n = 7
# new_data_dict['Weekly'] = new_data_dict['Weekly'].iloc[n:,]

#remove last row from weekly dataframe
n =1
new_data_dict['Weekly'] = new_data_dict['Weekly'][:-n]

# #remove first n rows from monthly dataframe
# n = 3
# new_data_dict['Monthly'] = new_data_dict['Monthly'].iloc[n:,]

#remove last row from quarterly dataframe
n=1
new_data_dict['Quarterly'] = new_data_dict['Quarterly'].iloc[:-n]

# #remove yearly dataframe from dict
# new_data_dict.pop('Yearly')


#update returns_dict with new_data
returns_dict = dm.append_dict(returns_dict, new_data_dict)

#create new returns report
rp.get_returns_report('returns_data_new', returns_dict)
