#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pickle
import numpy as np
import datetime
import os

data_filename = "/Yep/data/sleep_data_%s.pckl"
fig_name = "sandbox/.figures/tmp_sleep.png"

def get_hour_min(time_str):
    fields = time_str.split(':')
    return [int(fields[0]), int(fields[1])]

def get_year_month_day(date_str):
    fields = date_str.split('-')
    return [int(fields[0]), int(fields[1]), int(fields[2])]

def format_minutes_graph(x, pos):
    return "%dh%d" % divmod(x, 60)

class sleep_handler:
    def __init__(self,user):
        self.user = user
        self.today = datetime.date.today()
        self.asleep_hours = 0
        self.asleep_minutes = 0
        self.mean_sleep = 0
        try:
            f = open(data_filename % self.user, 'rb')
            self.dic = pickle.load(f)
            f.close()
        except IOError:
            self.dic = {'Date' : [], 'Asleep' : [], 'Woke' : [], 'Sleep' : np.array([])}

    def get_average(self):
        return divmod(int(self.mean_sleep), 60)

    def update_dic(self, colname, data):
        self.dic[colname].append(data)

    def get_dic(self):
        return self.dic

    def get_time_slept(self):
        return [self.asleep_hours, self.asleep_minutes]

    def save_data(self, dic=None):
        if dic is None:
            dic = self.dic
        f = open(data_filename % self.user, 'wb')
        pickle.dump(dic, f)
        f.close()
        os.sync()

    def add_new_time(self, time_bed_str, date_bed_str, time_up_str, date_up_str):
        toBed_time = datetime.datetime(get_year_month_day(date_bed_str)[0], get_year_month_day(date_bed_str)[1], get_year_month_day(date_bed_str)[2], get_hour_min(time_bed_str)[0], get_hour_min(time_bed_str)[1])
        upBed_time = datetime.datetime(get_year_month_day(date_up_str)[0],  get_year_month_day(date_up_str)[1],  get_year_month_day(date_up_str)[2],  get_hour_min(time_up_str)[0],  get_hour_min(time_up_str)[1])

        date = datetime.date(get_year_month_day(date_up_str)[0],  get_year_month_day(date_up_str)[1],  get_year_month_day(date_up_str)[2])
        
        asleep = upBed_time - toBed_time
        self.asleep_hours, self.asleep_minutes = divmod(divmod(asleep.seconds, 60)[0], 60)
        
        asleep_stored = self.asleep_hours * 60 + self.asleep_minutes

        # If today is already tracked, we don't add a new entry, just add the sleep time
        if date in self.dic['Date']:
            idx = self.dic['Date'].index(date)
            self.dic['Sleep'][idx] = self.dic['Sleep'][idx] + asleep_stored
        else:
            self.update_dic('Date', date)
            self.update_dic('Asleep', toBed_time)
            self.update_dic('Woke', upBed_time)
            self.dic['Sleep'] = np.append(self.dic['Sleep'], asleep_stored)

    def gen_graph_last_7days(self):
        len_dic = 7
        last_week_delta = datetime.timedelta(days=6)
        last_dates = [(self.today - datetime.timedelta(days=i)).strftime("%a") for i in range(6,-1,-1)]
        last_dates[-1] = "Tod"
        last_dates[-2] = "Yes"
        last_sleep = np.zeros(len_dic)
        for i in range(0, len(self.dic['Date'])):
            delta = self.today - self.dic['Date'][i]    
            if delta <= last_week_delta:
                last_sleep[6-delta.days] += self.dic['Sleep'][i]

        last_non_zero = np.array([i for i in last_sleep if i != 0])
        if len(last_non_zero) >= 1:
            self.mean_sleep = last_non_zero.mean()
        
        days = last_dates
        
        x = np.arange(len_dic)
        fig, axs = plt.subplots()
        axs.bar(x, last_sleep, color='b')
        axs.set_ylabel("Sleep time")
        
        formater = FuncFormatter(format_minutes_graph)
        axs.yaxis.set_major_formatter(formater)
        
        axs.get_xaxis().set_tick_params(direction='out')
        axs.xaxis.set_ticks_position('bottom')
        axs.set_xticks(np.arange(0, len(days)))
        axs.set_xticklabels(days)
        axs.set_xlabel('Day of the week')
       
        if self.mean_sleep != 0:
            axs.axhline(y=self.mean_sleep, color='0.5', linestyle='--', label="Avg: %dh%d" % (divmod(self.mean_sleep, 60)))
        
        axs.legend()
        fig.suptitle("Last 7 days sleep time")
        fig.savefig(fig_name, dpi=200)

    def get_fig_name(self):
        return ("/" + fig_name)
