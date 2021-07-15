# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.decay import get_decay_days
from EquityHedging.analytics.util import get_pos_neg_df
from EquityHedging.analytics import  util

HEDGE_METRICS_INDEX = ['Benefit Count','Benefit Median','Benefit Mean','Benefit Cum', 
                       'Downside Reliability','Upside Reliability',
                       'Convexity Count','Convexity Median','Convexity Mean','Convexity Cum',
                       'Cost Count','Cost Median','Cost Mean','Cost Cum',
                       'Decay Days (50% retrace)','Decay Days (25% retrace)','Decay Days (10% retrace)']

def get_hm_index_list(full_list=True):
    if full_list:
        return HEDGE_METRICS_INDEX
    else:
        return ['Benefit','Downside Reliability','Upside Reliability','Convexity','Cost', 'Decay']
    
def get_benefit_stats(df_returns, col_name):
    """
    Return count, mean, mode and cumulative of all positive returns
    less than the 98th percentile rank

    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.

    Returns
    -------
    benefit : dictionary
        {count: double, mean: double, median: double, cumulative: double}

    """
    
    #create a dataframe containing only the col_name strategy
    df_strat = dm.remove_na(df_returns, col_name)
    
    #compute the 98th percentile
    percentile = df_strat[col_name].quantile(.98)
    
    #get the all data that is less than the 98th percentile
    benefit_index = df_strat.index[df_strat[col_name] < percentile]
    benefit_ret = df_strat.loc[benefit_index]
    
    #filter out negative returns
    pos_ret = get_pos_neg_df(benefit_ret[col_name],True)
    
    #calculate hedge metrics
    benefit_count = pos_ret.count()
    benefit_mean = pos_ret.mean()
    benefit_med = pos_ret.median()
    benefit_cum = benefit_count*benefit_mean
    
    #create dictionary
    benefit = {'count': benefit_count, 
               'mean': benefit_mean, 
               'median': benefit_med,
               'cumulative': benefit_cum
               }

    return benefit

def get_convexity_stats(df_returns, col_name):
    """
    Return count, mean, mode and cumulative of all positive returns
    greater than the 98th percentile rank

    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.

    Returns
    -------
    convexity : dictionary
        {count: double, mean: double, median: double, cumulative: double}
    """
    
    #create a dataframe containing only the col_name strategy
    df_strat = dm.remove_na(df_returns, col_name)
    
    #compute the 98th percentile
    percentile = df_strat[col_name].quantile(.98)
    
    #get the all data that is greater than the 98th percentile
    convexity_index = df_strat.index[df_strat[col_name] > percentile]
    convexity_ret = df_strat.loc[convexity_index]
    
    #may not need this line since all the data may be positive already
    pos_ret = get_pos_neg_df(convexity_ret[col_name],True)
    
    #calculate hedge metrics
    convexity_count = pos_ret.count()
    convexity_mean = pos_ret.mean()
    convexity_med = pos_ret.median()
    convexity_cum = convexity_count*convexity_mean
    
    #create convexity dictionary
    convexity = {'count': convexity_count, 
                 'mean': convexity_mean , 
                 'median': convexity_med,
                 'cumulative': convexity_cum
                 }

    return convexity

def get_decay_stats(df_returns, col_name, freq):
    """
    Return decay stats of returns

    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.
    freq : string
        frequency.

    Returns
    -------
    decay_dict : dictionary
        {key: decay_percent, value: int)

    """
    
    #Compute decay values only if data is daily or weekly
    if dm.switch_freq_int(freq) >= 12:
        decay_half = get_decay_days(df_returns, col_name, freq)
        decay_quarter = get_decay_days(df_returns, col_name, freq, .25)
        decay_tenth = get_decay_days(df_returns, col_name, freq, .10)
    else:
        decay_half = 0
        decay_quarter = 0
        decay_tenth = 0
        
    #create decay dictionary
    decay_dict = {'half': decay_half, 
                  'quarter': decay_quarter, 
                  'tenth':decay_tenth
                  }
    
    return decay_dict

def get_cost_stats(df_returns, col_name):
    """
    Return count, mean, mode and cumulative of all negative returns

    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.

    Returns
    -------
    cost : dictionary
        {count: double, mean: double, median: double, cumulative: double}

    """
    
    #filter out positive returns
    neg_ret = get_pos_neg_df(df_returns[col_name] ,False)
    
    #calculate hedge metrics
    cost_count = neg_ret.count()
    cost_mean = neg_ret.mean()
    cost_med = neg_ret.median()
    cost_cum = cost_count*cost_mean
    
    #create cost dictionary
    cost = {'count': cost_count , 
            'mean': cost_mean , 
            'median': cost_med,
            'cumulative': cost_cum
            }
    
    return cost

def get_reliability_stats(df_returns, col_name):
    """
    Return correlation of strategy to equity bencmark downside returns and upside returns
    
    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.
        
    Returns
    -------
    reliability : dictionary
        dict{down(double), up(double)}.

    """
    
    #get the equity_id
    col_list = list(df_returns.columns)
    equity_id = col_list[0]
    
    #create dataframe containing only data when equity_id < 0
    equity_down = (df_returns[df_returns[equity_id] < 0])
    
    #comupte the correlation and get the reliability stat for the col_name strategy
    corr_d = equity_down.corr()
    reliability_d= corr_d[col_name].iloc[0]
    
    #create dataframe containing only data when equity_id > 0
    equity_up = (df_returns[df_returns[equity_id] > 0])
    
    #comupte the correlation and get the reliability stat for the col_name strategy
    corr_u = equity_up.corr()
    reliability_u = corr_u[col_name].iloc[0]
    
    #create reliability dictionary
    reliability={'down': reliability_d,
                 'up':reliability_u}
    
    return reliability

def get_hedge_metrics(df_returns, freq="1M", full_list=True):
    """
    Return a dataframe of hedge metrics

    Parameters
    ----------
    df_returns : dataframe
    freq : string, optional
        Frequency. The default is "1M".
    full_list: boolean, optional

    Returns
    -------
    df_hedge_metrics : dataframe
        
    """
    
    #create empty dictionary
    hedge_dict = {}
    
    if full_list:
        #loop through columns in df_returns to compute and store the hedge 
        #metrics for each strategy
        for col in df_returns.columns:
            benefit = get_benefit_stats(df_returns, col)
            reliability = get_reliability_stats(df_returns, col)
            convexity = get_convexity_stats(df_returns, col)
            cost = get_cost_stats(df_returns, col)
            decay = get_decay_stats(df_returns, col, freq)
            
            hedge_dict[col] = [benefit['count'],benefit['median'],benefit['mean'],
                               benefit['cumulative'],reliability['down'],reliability['up'],
                               convexity['count'],convexity['median'],convexity['mean'],
                               convexity['cumulative'],cost['count'],cost['median'],cost['mean'], 
                               cost['cumulative'],decay['half'],decay['quarter'],decay['tenth']]
    else:
        for col in df_returns.columns:
            benefit = get_benefit_stats(df_returns, col)
            reliability = get_reliability_stats(df_returns, col)
            convexity = get_convexity_stats(df_returns, col)
            cost = get_cost_stats(df_returns, col)
            decay = get_decay_days(df_returns, col, freq)
            
            hedge_dict[col] = [benefit['cumulative'],
                              reliability['down'],reliability['up'],
                              convexity['cumulative'], cost['cumulative'], decay]
    
    #Converts hedge_dict to a data grame
    df_hedge_metrics = util.convert_dict_to_df(hedge_dict, get_hm_index_list(full_list))
    return df_hedge_metrics

#TODO: format data to match data 
def get_hedge_metrics_to_normalize(returns, equity_bmk, notional_weights, weighted_hedge = False):
    '''
    Parameters
    ----------
    returns : dict
        dictionary containing returns data of strategies across different frequencies
    equity_bmk : string
        SPTR, M1WD, SPX

    Returns
    -------
    Data Frame with specified hedge metrics of strategies. 
    '''
    #Index weekly returns and obtain weighted hedges
    weekly_ret = returns['Weekly'].copy()
    
    if weighted_hedge == True:
        weekly_ret = util.get_weighted_hedges(weekly_ret, notional_weights)
        
    #create empty dictionary
    hedge_dict = {}
    
    #Calculate only the hedge metrics needed in normalization and ranking
    for col in weekly_ret.columns:
        benefit = get_benefit_stats(weekly_ret, col)['cumulative']
        reliability = get_reliability_stats(weekly_ret, col)
        convexity = get_convexity_stats(weekly_ret, col)['cumulative']
        cost = get_cost_stats(weekly_ret, col)['cumulative']
        decay = get_decay_stats(weekly_ret, col, freq='1W')['half']
        
        hedge_dict[col] = [benefit,
                          reliability['down'],reliability['up'],
                          convexity, cost, decay]
    
    #Converts hedge_dict to a data grame
    df_hedge_metrics = util.convert_dict_to_df(hedge_dict,get_hm_index_list(False))
    
    
    
    #drop the equity benchmark
    #NOTES: Don't need to specifiy equity bmk
    df_hedge_metrics.drop(equity_bmk, axis = 1, inplace = True)
    
    df = df_hedge_metrics.transpose()
    return df

