#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pickle
import numpy as np
import datetime

data_filename = "/Yep/data/exp_data_%s.pckl"

pay_methods = ["Compte Commun", "Cash", "Card Tony", "Card AC", "Cheques Repas"]
types = ["Groceries", "Car", "Holidays", "Restos", "Fast Food", "Epargne", "Insurance", "Gifts", "Books", "Entertainment", "Actis", "Work", "Drank & Drugs"]

def get_year_month_day(date_str):
    fields = date_str.split('-')
    return [int(fields[0]), int(fields[1]), int(fields[2])]

class exp_handler:
    def __init__(self, user):
        self.user = user
        try:
            f = open(data_filename % self.user, 'rb')
            self.dic = pickle.load(f)
            f.close()
        except IOError:
            self.dic = {'Date' : [], 'Type' : [], 'Method': [], 'Amount' : np.array([])}

    def update_dic(self, colname, data):
        self.dic[colname].append(data)

    def get_types(self):
        return types
    
    def get_pay_methods(self):
        return pay_methods

    def save_data(self):
        f = open(data_filename % self.user, 'wb')
        pickle.dump(self.dic, f)
        f.close()

    def add_new_exp(self, date_str, amount_float, exp_type, pay_method):
        self.today = datetime.date(get_year_month_day(date_str)[0], get_year_month_day(date_str)[1], get_year_month_day(date_str)[2])
        
        self.update_dic('Date', self.today)
        self.update_dic('Type', exp_type)
        self.update_dic('Method', pay_method)
        self.dic['Amount'] = np.append(self.dic['Amount'], amount_float)
