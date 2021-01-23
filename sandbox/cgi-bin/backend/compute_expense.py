#!/usr/bin/env python

import pickle
import datetime
import numpy as np
import os

data_filename = "/Yep/data/exp_data_%s.pckl"

pay_methods = ["Compte Commun", "Cash", "Card Tony", "Card AC", "Cheques Repas"]
benefs = ["Both", "Tony", "AC"]
types = ["Groceries", "Car", "Holidays", "Restos", "Fast Food", "Epargne", "Insurance", "Gifts", "Books", "Entertainment", "Actis", "Work", "Drank & Drugs", "Cat", "Extra"]

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
            self.dic = {'Date' : [], 'Type' : [], 'Method': [], 'Benef': [], 'Amount' : np.array([])}

    def update_dic(self, colname, data):
        self.dic[colname].append(data)

    def get_types(self):
        return types
    
    def get_benefs(self):
        return benefs
    
    def get_pay_methods(self):
        return pay_methods

    def get_dic(self):
        return self.dic

    def save_data(self, dic=None):
        if dic is None:
            dic = self.dic
        f = open(data_filename % self.user, 'wb')
        pickle.dump(dic, f)
        f.close()
        os.sync()

    def add_new_exp(self, date_str, amount_float, exp_type, pay_method, benef):
        self.today = datetime.date(get_year_month_day(date_str)[0], get_year_month_day(date_str)[1], get_year_month_day(date_str)[2])
        
        self.update_dic('Date', self.today)
        self.update_dic('Type', exp_type)
        self.update_dic('Method', pay_method)
        self.update_dic('Benef', benef)
        self.dic['Amount'] = np.append(self.dic['Amount'], amount_float)
