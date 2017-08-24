import sys
import StockTool
from datetime import datetime, timedelta
import os


if __name__ == '__main__':
# 	sys.path.append('')
# 	from core import *
	
	
	
	# test = StockTool.StockInfo('2330')
# 	print(test.get_StockNumber())
# 	EndDate = datetime(datetime.now().year,datetime.now().month, 1)
# 	StartDate = datetime(datetime.now().year-5,datetime.now().month, 1)
# 	test.fetch_StockPrice(StartDate, EndDate)
# 	print(test.get_StockPrice().tail())
# 	
	# Now = datetime.now()
	Machine = StockTool.Crawler()
	# test.get_tse_data(datetime.now())
	

	#Start from 1994(093)/02/11
	Startdate = datetime(2009, 2, 11)
	# datediff = timedelta(days=1)
	
	tem = Machine.get_tse_one_day(Startdate)
	print(type(tem))