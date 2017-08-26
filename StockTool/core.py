

from . import helpers

import pandas as pd
import numpy as np
from pandas import DataFrame, Series

from pandas_datareader import data
from datetime import datetime, timedelta


import re
import os
import requests
import time






class StockInfo():
	def __init__(self, StockNumber):
		if isinstance(StockNumber, str) is False:
			print('StockNumber must be string')
			self.__StockNumber = '2330.TW'
			
		else:
			self.__StockNumber = StockNumber+'.TW'
	
	def get_StockNumber(self):
		return self.__StockNumber
		
	def fetch_StockPrice(self, StartTime, EndTime):
# 		self.__StockPrice = data.DataReader(self.__StockNumber, 
# 											'yahoo',StartTime, EndTime)
		self.__StockPrice = data.DataReader(self.__StockNumber, 
											'yahoo',StartTime, EndTime)
		
	def get_StockPrice(self):
		return self.__StockPrice
	
	def fetch_StockActions(self, StartTime, EndTime):
		self.__StockActions = data.DataReader(self.__StockNumber,
											'yahoo-actions',StartTime, EndTime)
	def get_StockActions(self):
		return self.__StockActions
		
		
class Crawler():
	def __init__(self, prefix='data'):
		if not os.path.isdir(prefix):
			os.mkdir(prefix)
		self.prefix = prefix
		# pass
	
	def get_tse_one_day(self, spec_date):
		date_str = '{0}{1:02d}{2:02d}'.format(spec_date.year, spec_date.month, spec_date.day)
		url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX'

		query_params = {
			'date': date_str,
			'response': 'json',
			'type': 'ALL',
			'_': str(round(time.time() * 1000) - 500)
		}

		# Get json data
		page = requests.get(url, params=query_params)

		if not page.ok:
			logging.error("Can not get TSE data at {}".format(date_str))

		content = page.json()
		# print(content)
		# key = 'Nodata'
		isoffday = True
		for key in content.keys():
			if isinstance(content[key], list):
				if len(content[key][0]) == 16:
					isoffday = False
					break
		if isoffday:
			print('No data at this day %4d/%02d/%02d'% 
					(spec_date.year,spec_date.month, spec_date.day))
			return -1

		# For compatible with original data
		# date_str_mingguo = '{0}/{1:02d}/{2:02d}'.format(spec_date.year - 1911,\
		# 	spec_date.month, spec_date.day)

		data_df = DataFrame(data=content[key], 
							columns=['code','name','volume','transaction','turnover',
									 'open','high','low','close','UD','difference',
									 'last_buy', 'last_buy_volume',
									 'last_sell','last_sell_volume','PE_ratio'])

		data_df = data_df.applymap(lambda x: re.sub(",","",x))# clear comma
		data_df.replace({'UD':{'<p style= color:red>+</p>':'+',
							   '<p style= color:green>-</p>':'-'}},
						inplace=True)

		return data_df
	
	def get_otc_one_day(self, spec_date):
		date_str = '{0}/{1:02d}/{2:02d}'.format(spec_date.year-1911, spec_date.month, spec_date.day)
		
		ttime = str(int(time.time()*100))
		url = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d={}&_={}'.format(date_str, ttime)
		page = requests.get(url)

		if not page.ok:
			logging.error("Can not get OTC data at {}".format(date_str))

		content = page.json()
		# print(content)
		# key = 'Nodata'
		if (len(content['aaData']) + len(content['mmData'])) == 0:
			print('No data at this day ' + date_str)
			return -1
		data_df = DataFrame(data=content['aaData'] + content['mmData'], 
							columns=['code','name','close','difference','open',
									 'high','low','avg','volume','turnover',
									 'transaction','last_buy',
									 'last_sell','NumOfShare','NextRefPrice',
									 'NextUpperPrice', 'NextLowerPrice'])

		data_df = data_df.applymap(lambda x: re.sub(",","",x))# clear comma
		
		return data_df

	def check_all_tse_data(self):
		Filelist = os.listdir(self.prefix)
		if 'offday.xlsx' in Filelist:
			offday_ser = pd.read_excel(self.prefix + '/offday.xlsx')
			offday_ser = offday_ser['date'].copy()
		else:
			offday_ser = Series(name='date', data='First')

		offday_update = False
		lastday_update = False

		Now = datetime.now()
		Nowdate = datetime(Now.year, Now.month, Now.day)

		if 'lastday.txt' in Filelist:
			with open(self.prefix + '/lastday.txt', 'r') as f:
				read_data = f.read()
				f.close()
				Startdate = datetime(int(read_data[0:4]), 
									int(read_data[4:6]), 
									int(read_data[6:8]))
		else:
			#Start from 2004(093)/02/11
			Startdate = datetime(2004, 2, 11)
		
		datediff = timedelta(days=1)
		
		while Startdate <= Nowdate:
			date_str = '{0}{1:02d}{2:02d}'.\
					format(Startdate.year-1911,Startdate.month, Startdate.day)
			print('Read ' + date_str)
			if ('%s.xlsx' %(date_str)) not in Filelist:# not in FileList
				if (offday_ser != date_str).all():# not a offday
					lastday_update = True
					data_df = self.get_tse_one_day(Startdate) # collect data
					if isinstance(data_df, DataFrame):# success
						data_df.to_excel('{0}/{1}.xlsx'.format(self.prefix,date_str))# save data
					else:# is an offday, update offday series
						offday_ser.set_value( len(offday_ser), date_str)
						offday_update = True
						print(date_str + 'is an offday')
				else:
					print(date_str + ' is known as an offday')
			else:
				print(date_str + ' is in FileList')
			Startdate = Startdate + datediff

		if offday_update:
			offday_ser.to_excel(self.prefix + '/offday.xlsx')

		if lastday_update:
			with open(self.prefix + '/lastday.txt', 'w') as f:
				# Nowdate += timedelta(days=-1)
				date_str = '{0}{1:02d}{2:02d}'.\
					format(Nowdate.year,Nowdate.month, Nowdate.day)
				f.write(date_str)
				f.close()

	def check_all_otc_data(self):
		Filelist = os.listdir(self.prefix)
		if 'offdayOTC.xlsx' in Filelist:
			offday_ser = pd.read_excel(self.prefix + '/offdayOTC.xlsx')
			offday_ser = offday_ser['date'].copy()
		else:
			offday_ser = Series(name='date', data='First')

		offday_update = False
		lastday_update = False

		Now = datetime.now()
		Nowdate = datetime(Now.year, Now.month, Now.day)

		if 'lastdayOTC.txt' in Filelist:
			with open(self.prefix + '/lastdayOTC.txt', 'r') as f:
				read_data = f.read()
				f.close()
				Startdate = datetime(int(read_data[0:4]), 
									int(read_data[4:6]), 
									int(read_data[6:8]))
		else:
			#Start from 2007(096)/04/23
			Startdate = datetime(2007, 4, 23)
		
		datediff = timedelta(days=1)
		
		while Startdate <= Nowdate:
			date_str = '{0}{1:02d}{2:02d}'.\
					format(Startdate.year-1911,Startdate.month, Startdate.day)
			print('Read ' + date_str + ' OTC')
			if ('%sOTC.xlsx' %(date_str)) not in Filelist:# not in FileList
				if (offday_ser != date_str).all():# not a offday
					lastday_update = True
					data_df = self.get_otc_one_day(Startdate) # collect data
					if isinstance(data_df, DataFrame):# success
						data_df.to_excel('{0}/{1}OTC.xlsx'.format(self.prefix,date_str))# save data
					else:# is an offday, update offday series
						offday_ser.set_value( len(offday_ser), date_str)
						offday_update = True
						print(date_str + 'is an offday')
				else:
					print(date_str + ' is known as an offday')
			else:
				print(date_str + ' is in FileList')
			Startdate = Startdate + datediff

		if offday_update:
			offday_ser.to_excel(self.prefix + '/offdayOTC.xlsx')

		if lastday_update:
			with open(self.prefix + '/lastdayOTC.txt', 'w') as f:
				# Nowdate += timedelta(days=-1)
				date_str = '{0}{1:02d}{2:02d}'.\
					format(Nowdate.year,Nowdate.month, Nowdate.day)
				f.write(date_str)
				f.close()











	

