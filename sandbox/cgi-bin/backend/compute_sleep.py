#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pickle
import numpy as np
import datetime

data_filename = "/Yep/data/sleep_data.pckl"
fig_name = "sandbox/figures/%s.png"

def get_hour_min(time_str):
    fields = time_str.split(':')
    return [int(fields[0]), int(fields[1])]

def get_year_month_day(date_str):
    fields = date_str.split('-')
    return [int(fields[0]), int(fields[1]), int(fields[2])]

def format_minutes_graph(x, pos):
    return "%dh%d" % divmod(x, 60)

class sleep_handler:
    def __init__(self):
        self.today = datetime.date.today()
        self.asleep_hours = 0
        self.asleep_minutes = 0
        try:
            f = open(data_filename, 'rb')
            self.dic = pickle.load(f)
            f.close()
        except IOError:
            self.dic = {'Date' : [], 'Asleep' : [], 'Woke' : [], 'Sleep' : np.array([])}

    def get_average(self):
        return divmod(int(self.mean_sleep), 60)

    def update_dic(self, colname, data):
        self.dic[colname].append(data)

    def get_time_slept(self):
        return [self.asleep_hours, self.asleep_minutes]

    def save_data(self):
        f = open(data_filename, 'wb')
        pickle.dump(self.dic, f)
        f.close()

    def add_new_time(self, time_bed_str, date_bed_str, time_up_str, date_up_str):
        # Assume we went to bed the day before
        daydiff = datetime.timedelta(days=1)
        
        # Get date
        yesterday = self.today - daydiff
        
        toBed_time = datetime.datetime(get_year_month_day(date_bed_str)[0], get_year_month_day(date_bed_str)[1], get_year_month_day(date_bed_str)[2], get_hour_min(time_bed_str)[0], get_hour_min(time_bed_str)[1])
        upBed_time = datetime.datetime(get_year_month_day(date_up_str)[0],  get_year_month_day(date_up_str)[1],  get_year_month_day(date_up_str)[2],  get_hour_min(time_up_str)[0],  get_hour_min(time_up_str)[1])

        # Update today variable with wake up date
        self.today = datetime.date(get_year_month_day(date_up_str)[0],  get_year_month_day(date_up_str)[1],  get_year_month_day(date_up_str)[2])
        
        asleep = upBed_time - toBed_time
        self.asleep_hours, self.asleep_minutes = divmod(divmod(asleep.seconds, 60)[0], 60)
        
        asleep_stored = self.asleep_hours * 60 + self.asleep_minutes

        # If today is already tracked, we don't add a new entry, just add the sleep time
        if self.today in self.dic['Date']:
            idx = self.dic['Date'].index(self.today)
            self.dic['Sleep'][idx] = self.dic['Sleep'][idx] + asleep_stored
        else:
            self.update_dic('Date', self.today)
            self.update_dic('Asleep', toBed_time)
            self.update_dic('Woke', upBed_time)
            self.dic['Sleep'] = np.append(self.dic['Sleep'], asleep_stored)

    def gen_graph_last_7days(self):
        len_dic = 7
        if len(self.dic['Date']) < 7:
            len_dic = len(self.dic['Date'])
        last_dates = self.dic['Date'][-len_dic:]
        last_sleep = self.dic['Sleep'][-len_dic:]
        
        self.mean_sleep = last_sleep.mean()
        days = [i.strftime("%a") for i in last_dates]
        
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
        
        axs.axhline(y=self.mean_sleep, color='0.5', linestyle='--')
        
        fig.suptitle("Sleep time")
        fig.savefig(fig_name % str(self.today), dpi=200)

    def get_fig_name(self):
        return ("/" + fig_name % self.today)
