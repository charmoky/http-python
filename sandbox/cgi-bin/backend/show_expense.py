#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib._color_data as mcd
import numpy as np
import datetime
import random
import pickle
import os

fig_name = "sandbox/.figures/tmp_exp_%s.png"

color_pckl = "/Yep/data/exp_colors_%s.pckl"


class exp_shower:
    def __init__(self, user, dic, types, pay_methods, benefs):
        self.benefs = benefs
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
        self.last_12_mth = np.zeros((12, len(types)))
        self.own_matrix_last_2mth = np.zeros((2, len(benefs)-1, len(benefs)-1))

        try:
            f = open(color_pckl % user, 'rb')
            self.types_colors = pickle.load(f)
            f.close()
        except:
            self.types_colors = random.sample(mcd.XKCD_COLORS.keys(), len(mcd.XKCD_COLORS.keys()))
            f = open(color_pckl % user, 'wb')
            pickle.dump(self.types_colors, f)
            f.close()

    def get_colors_filename():
        return (color_pckl % self.user)

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
        self.last_day = datetime.date.today() 

        for i in range(0, len(self.dic['Date'])):
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

            delta_months = (self.last_day.year - self.dic['Date'][i].year) * 12 + (self.last_day.month - self.dic['Date'][i].month)
            if delta_months <= 12:
                self.last_12_mth[11-delta_months][type_idx] += amount

            if delta_months <= 1:
                # Compute matrix of who-owns-who
                #  3 cases of owning: 
                #     1. Paid with Card which is not your own
                #     2. Paid by compte commun for not Both
                #     3. Paid by with Card for Both
                benef_idx = self.benefs.index(benef)-1
                if self.dic['Benef'][i] != "Both" and self.dic['Method'][i] == "Compte Commun":
                    for own in self.benefs:
                        idx_i = self.benefs.index(own)-1
                        if idx_i != benef_idx[1:]:
                            self.own_matrix_last_2mth[delta_months][benef_idx][idx_i] += amount
                
                if self.dic['Method'][i].find("Card") != -1:
                    if benef == "Both":
                        for payer in self.benefs:
                            if self.dic['Method'][i].find("%s" % payer) != -1:
                                break
                        idx_payer = idx_i = self.benefs.index(payer)-1
                        
                        for own in self.benefs[1:]:
                            idx_i = self.benefs.index(own)-1
                            if idx_i != idx_payer:
                                self.own_matrix_last_2mth[delta_months][idx_i][idx_payer] += amount
                            
                    elif self.dic['Method'][i] != ("Card %s" % benef):
                        for own in self.benefs:
                            if self.dic['Method'][i].find("%s" % own) != -1:
                                break
                        idx_i = self.benefs.index(own)-1
                        self.own_matrix_last_2mth[delta_months][benef_idx][idx_i] += amount
        

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
        
            ax.bar(ind, last_7days_trans[i].tolist(), bottom=bottom.tolist(), label=exp_type, color=self.types_colors[i])
            bottom += last_7days_trans[i]
        
        mean = self.last_7days.sum(axis=1).mean()
        ax.axhline(y=mean, color='0.5', linestyle='--', label="Avg: %.2f€" % mean)
            
        ax.legend()
        ax.set_xticks(np.arange(0, len(days)))
        ax.set_xticklabels(days)
        ax.set_ylabel("Amount €")
        ax.set_xlabel('Day of the week')
        
        fig.suptitle("Expense of last 7 days : %.2f€" % self.last_7days.sum())
        fig.savefig(fig_name % ("week"), dpi=200)

    def gen_graphs_last_12months(self):
        months_idx = [((self.last_day.month-i) % 12) if ((self.last_day.month-i) % 12) != 0 else 12 for i in range (11,-1,-1)]
        months = [self.last_day.replace(day=1, month=i).strftime("%b") for i in months_idx]

        ind = np.arange(12)
        fig, ax = plt.subplots()
        
        ax.bar(ind, self.last_12_mth.sum(axis=1).tolist())
        
        mean = self.last_12_mth.sum(axis=1).mean()
        ax.axhline(y=mean, color='0.5', linestyle='--', label="Avg: %.2f€" % mean)
            
        ax.legend()
        ax.set_xticks(np.arange(0, len(months)))
        ax.set_xticklabels(months)
        ax.set_ylabel("Amount €")
        ax.set_xlabel('Previous Months')
        
        fig.suptitle("Expense of last 12 months : %.2f€" % self.last_12_mth.sum())
        fig.savefig(fig_name % ("12_months"), dpi=200)

    def gen_pie_charts(self, data, labels, colors, fig_title, fig_filename):
        norm_data = data
        norm = []
        labels_filt = []
        colors_filt = []
        for i,_ in enumerate(labels):
            if norm_data[i] == 0:
                continue
            norm.append(norm_data[i])
            labels_filt.append(labels[i])
            colors_filt.append(colors[i])

        explode = np.ones(len(norm)) * 0.05
        fig, ax = plt.subplots()
        
        def show_full_value(pct):
            if pct < 4:
                return ""
            elif pct > 10:
                return "%.1f€\n%.1f%%" % (pct/100*data.sum(), pct)
            else:
                return "%.1f%%" % (pct)

        ax.pie(norm, labels=labels_filt, explode=explode, normalize=True, autopct=show_full_value, colors=colors_filt)
        fig.suptitle(fig_title)
        fig.savefig(fig_filename, dpi=200)


    def gen_charts(self):
        self.make_arrays()
        self.gen_graphs_last_7days()
        self.gen_graphs_last_12months()

        title = "Expense of the month : %.2f€" % self.by_types_mth.sum()
        fig_filename = fig_name % ("month")
        self.gen_pie_charts(self.by_types_mth, self.types, self.types_colors, title, fig_filename)

        title = "Expense of the year : %.2f€" % self.by_types_yr.sum()
        fig_filename = fig_name % ("year")
        self.gen_pie_charts(self.by_types_yr, self.types, self.types_colors, title, fig_filename)

    def get_owns_what_month(self, user, benef, delta_months=0):
        user_idx = self.benefs.index(user)-1
        benef_idx = self.benefs.index(benef)-1
        return self.own_matrix_last_2mth[delta_months][user_idx][benef_idx] - self.own_matrix_last_2mth[delta_months][benef_idx][user_idx]

    def get_fig_name(self):
        return [("/" + fig_name % ("week")), 
            ("/" + fig_name % ("month")),
            ("/" + fig_name % ("12_months")),
            ("/" + fig_name % ("year"))]


