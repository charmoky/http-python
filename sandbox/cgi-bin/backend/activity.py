#!/usr/bin/env python

import pickle
import os
import datetime

data_filename = "/Yep/data/activity_data.pckl"

class activity_tracker:
    def __init__(self,user):
        self.user = user
        self.today = datetime.date.today()
        try:
            f = open(data_filename, 'rb')
            self.dic = pickle.load(f)
            f.close()
        except IOError:
            self.dic = {'Date' : [], 'Activity' : [], 'Link' : [], 'Description' : [], 'Adder' : []}

    def save_data(self, dic=None):
        if dic is None:
            dic = self.dic
        f = open(data_filename, 'wb')
        pickle.dump(dic, f)
        f.close()
        os.sync()

    def update_dic(self, colname, data):
        self.dic[colname].append(data)

    def add_activity(self, Activity, Link=None, Description=None):
            self.update_dic('Date', self.today)
            self.update_dic('Activity', Activity)
            self.update_dic('Link', Link)
            self.update_dic('Description', Description)
            self.update_dic('Adder', self.user)

    def get_dic(self):
        return self.dic
