import sys
import StockTool
from datetime import datetime, timedelta
import os


if __name__ == '__main__':

	Machine = StockTool.Crawler()

	#Start from 1994(093)/02/11
	Machine.check_all_tse_data()

