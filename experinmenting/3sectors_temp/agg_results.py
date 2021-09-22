#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 14:52:41 2021

@author: chengyu
"""

import pandas as pd 
import ast
from utils import get_current_res_folder
import os 


def convert_dict_columns(df,colum_name):
    if isinstance(df[colum_name][0],str):
        df[colum_name] = df[colum_name].map(ast.literal_eval)
        # reset the index if the index is not unique integers from 0 to n-1
        # df.reset_index(inplace=True)  # uncomment if needed
        x = pd.json_normalize(df[colum_name])
        df = df.join(x)
        df.drop(columns=[colum_name], inplace=True)
        return df
    
def post_process_firm_log(f,out_f=None):
    df = pd.read_csv(f)
    df = convert_dict_columns(df,'out_iter_memory_current')
    df['n_labor_hired'] = df['labor_hired'].apply(len)
    df['n_product_sold'] = df['actual_production']-df['balance_sheet.consumption_good']
    if out_f:
        df.to_csv(out_f)

    return df

def post_process_hh_log(f,out_f=None):
    df = pd.read_csv(f)
    df = convert_dict_columns(df,'out_balance_sheet')
    if out_f:
        df.to_csv(out_f)
    return df

def post_process_bank_log(f,out_f=None):
    df = pd.read_csv(f)
    df = convert_dict_columns(df,'out_financial_account')
    if out_f:
        df.to_csv(out_f)
    return df

def get_round(r):
    inp = str(r)
    if len(inp)==2:
        return 0 
    else:
        return inp[:-2]

def calculate_firm_aggregate(df,out_f = None):
    """
    aggregate firm df for  global statistics 

    """
    df['iter'] = df['round'].apply(get_round)
    ## get total revenue and cost for global averaging
    df['total_labor_cost'] = df['price_labor']*df['n_labor_hired']
    df['total_revenue'] = df['price_consumption_good']*df['n_product_sold']
    
    ## set up variables for aggregating 
    sum_columns = ['planned_production','labor_needed',
                   'actual_production','new_credit_received',
                   'balance_sheet.money','balance_sheet.debt',
                   'total_labor_cost','total_revenue',
                   'n_labor_hired','n_product_sold']
    
    agg_dict = {k:'sum' for k in sum_columns}
    agg_df = df.groupby('iter').agg(agg_dict)
    
    ## calculate average prices 
    agg_df['avg_consumption_price'] = agg_df['total_revenue'] / agg_df['n_product_sold']
    agg_df['avg_labor_price'] = agg_df['total_labor_cost'] / agg_df['n_labor_hired']
    
    if out_f:   
        agg_df.to_csv(out_f)
        
    return agg_df


def calculate_hh_aggregate(df,out_f = None):
    """
    aggregate hh df for  global statistics 

    """
    df['iter'] = df['round'].apply(get_round)
    
    df['employed'] = df['employer'].notnull()
    sum_columns = ['accumulated_utility','money','employed']
    agg_dict = {k:'sum' for k in sum_columns}
    agg_dict['index']='count'
    agg_df = df.groupby('iter').agg(agg_dict)
    agg_df.rename(columns={'index':"total_labor"},inplace=True)

    ## calculate unemployment rate
    agg_df['unemployment_rate'] = 1- agg_df['employed']/agg_df['total_labor']
    
    return agg_df

#%%
if __name__ == "__main__":
    ## get result folder 
    res_folder = get_current_res_folder('./result')
    
    ## process firms
    f = os.path.join(res_folder,'panel_firm.csv')
    out_f = os.path.join(res_folder,'panel_firm_processed.csv')
    firm_df = post_process_firm_log(f,out_f)
        ## product global statistics 
    agg_firm_df = calculate_firm_aggregate(firm_df) 
    agg_firm_df[['avg_consumption_price','avg_labor_price',
                 'balance_sheet.money','balance_sheet.debt',
                 'n_labor_hired','labor_needed']].plot(title='Frims agg statistics',subplots=True)
    agg_firm_df[['actual_production','n_product_sold']].plot(title='Frims agg statistics 2',subplots=False)
    
    ## process household 
    f = os.path.join(res_folder,'panel_household.csv')
    out_f = os.path.join(res_folder,'panel_household_processed.csv')
    hh_df = post_process_hh_log(f,out_f)
        ## product global statistics 
    agg_hh_df = calculate_hh_aggregate(hh_df)
    agg_hh_df[['money','accumulated_utility','unemployment_rate']].plot(title='Hourseholds agg statistics',subplots=True)
    
    ## process bank 
    f = os.path.join(res_folder,'panel_bank.csv')
    out_f = os.path.join(res_folder,'panel_bank_processed.csv')
    bank_df = post_process_bank_log(f,out_f)
    bank_df[['policy_rate','outstanding_loan','interest_payment','bad_loan']].plot(title='Bank agg statistics',subplots=True)


    
    
    
    