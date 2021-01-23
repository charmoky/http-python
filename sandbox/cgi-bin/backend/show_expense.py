#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import datetime

import os

fig_name = "sandbox/figures/exp_%s_%s_%s.png"


class exp_shower:
    def __init__(self, user, dic, types, pay_methods):
        self.user = user
        self.dic = dic
        self.types = types
        self.pay_methods = pay_methods
        self.by_types_mth = np.zeros(len(types))
        self.by_types_yr = np.zeros(len(types))
        self.by_method_mth = np.zeros(len(pay_methods))
        self.by_method_yr = np.zeros(len(pay_methods))
        self.last_7days = np.zeros((7, len(types)))
        self.last_day = datetime.date.today()

    def is_benef_tracked(self, benef):
        if benef == "Both":
            return True
        if benef == "Tony" and self.user == "shep":
            return True
        if benef == "AC" and self.user == "tupai":
            return True
        return False

    def get_amount(self, amount, benef):
        if benef == "Both":
            return amount/2.0
        return amount
   
    def make_arrays(self):
        last_week_delta = datetime.timedelta(days=6)
        dates = self.dic['Date'].copy()
        dates.sort()
        self.last_day = dates[-1]

        for i in range(0, len(dates)):
            benef = self.dic['Benef'][i]
            if not self.is_benef_tracked(benef):
                continue
    
            type_idx = self.types.index(self.dic['Type'][i])
            meth_idx = self.pay_methods.index(self.dic['Method'][i])
            amount = self.get_amount(self.dic['Amount'][i], benef)
            if self.dic['Date'][i].year == self.last_day.year:
                self.by_types_yr[type_idx] += amount
                self.by_method_yr[meth_idx] += amount
            if self.dic['Date'][i].month == self.last_day.month:
                self.by_types_mth[type_idx] += amount
                self.by_method_mth[meth_idx] += amount
        
            delta = self.last_day - self.dic['Date'][i]    
            if delta <= last_week_delta:
                self.last_7days[6-delta.days][type_idx] += amount

    def gen_graphs_last_7days(self):
        days = [(self.last_day - datetime.timedelta(days=i)).strftime("%a") for i in range(6,-1,-1)]
        days[-1] = "Tod"
        days[-2] = "Yes"

        ind = np.arange(7)
        last_7days_trans = np.transpose(self.last_7days)
        fig, ax = plt.subplots()
        bottom=np.zeros(7)
        for i, exp_type in enumerate(self.types):
            if last_7days_trans[i].sum() == 0:
                continue
        
            ax.bar(ind, last_7days_trans[i].tolist(), bottom=bottom.tolist(), label=exp_type)
            bottom += last_7days_trans[i]
        
        mean = self.last_7days.sum(axis=1).mean()
        ax.axhline(y=mean, color='0.5', linestyle='--', label="Avg: %.2f€" % mean)
            
        ax.legend()
        ax.set_xticks(np.arange(0, len(days)))
        ax.set_xticklabels(days)
        ax.set_ylabel("Amount €")
        ax.set_xlabel('Day of the week')
        
        fig.suptitle("Expense of last 7 days : %.2f€" % self.last_7days.sum())
        fig.savefig(fig_name % ("week", self.user, str(self.last_day)), dpi=200)

    def gen_pie_charts(self, data, labels, fig_title, fig_filename):
        norm_data = data/data.sum()
        norm = []
        labels_filt = []
        for i,_ in enumerate(labels):
            if norm_data[i] == 0:
                continue
            norm.append(norm_data[i])
            labels_filt.append(labels[i])

        explode = np.ones(len(norm)) * 0.02
        fig, ax = plt.subplots()
        
        def show_full_value(pct):
            return "%.1f€" % (pct/100*data.sum())

        ax.pie(norm, labels=labels_filt, explode=explode, normalize=False, autopct=show_full_value)
        fig.suptitle(fig_title)
        fig.savefig(fig_filename, dpi=200)


    def gen_charts(self):
        self.make_arrays()
        self.gen_graphs_last_7days()

        title = "Expense of last month : %.2f€" % self.by_types_mth.sum()
        fig_filename = fig_name % ("month", self.user, self.last_day.strftime("%y_%m"))
        self.gen_pie_charts(self.by_types_mth, self.types,title, fig_filename)
        
        title = "Expense of last year : %.2f€" % self.by_types_yr.sum()
        fig_filename = fig_name % ("year", self.user, self.last_day.strftime("%y"))
        self.gen_pie_charts(self.by_types_yr, self.types, title, fig_filename)

    def get_fig_name(self):
        return [("/" + fig_name % ("week", self.user, str(self.last_day))), 
            ("/" + fig_name % ("month", self.user, self.last_day.strftime("%y_%m"))),
            ("/" + fig_name % ("year", self.user, self.last_day.strftime("%y")))]


