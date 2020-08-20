import json
from stackapi import StackAPI
from ordered_set import OrderedSet
import pandas as pd
import time
import calendar
import datetime

APP_KEY = '' ### redacted
ACCESS_TOKEN = '' ### redacted



valid_sites = ['math', 'politics', 'biology', 'cooking', 'history', 'cs']
n = 500
#https://api.stackexchange.com/2.2/questions?fromdate=2019-01-01&todate=2019-01-31&order=desc&sort=activity&site=biology&pagesize=100

def is_ascii(s):
	return all(ord(c) < 128 for c in s)

def date(year, month, day):
	return int((datetime.datetime(year, month, day) - datetime.datetime(1970,1,1)).total_seconds())


def binary_df(df):
	dummy = df.iloc[:,2].str.get_dummies(sep=',')
	dummy.insert(0, 'question_id', df.iloc[:,0])
	dummy.insert(1, 'title', df.iloc[:,1])
	return dummy

def get_questions_and_tags(topic, pageSize, fromD, toD):
	df = pd.DataFrame(columns=['qId', 'title', 'tags'])
	method = 'questions'
	SITE = StackAPI(topic, key=APP_KEY, access_token=ACCESS_TOKEN)
	response = SITE.fetch(method, pagesize=pageSize, fromdate=fromD, todate=toD)
	items = response['items']
	for i, item in enumerate(items):
		if is_ascii(item['title']):
			df.loc[i] = [item['question_id'], item['title'].replace(',', ' '), ','.join(item['tags'])]
	return df
		



start_time = time.time()

def create_data():

	for site in valid_sites:
		df = pd.DataFrame(columns=['qId', 'title', 'tags'])
		for i in range(1, 12):
			new_df = get_questions_and_tags(site, n/5, date(2018, i, 1), date(2018, i+1, 1))
			df = df.append(new_df, ignore_index=True)
			
		df.drop_duplicates('qId', inplace = True)
		binary = binary_df(df)

		binary.to_csv('{}_data.csv'.format(site))

		col = binary.ix[:,0]
		t = ''
		if len(col) == len(set(col)):
			t = 'gucci'
		else:
			t = 'fook'

		print '{} with {} columns; all {}'.format(site, len(col), t)


def create_test():
	
	for site in valid_sites:
		df = get_questions_and_tags(site, n/5, date(2019, 1, 1), date(2019, 2, 1))
		df.to_csv('test_data/{}_test.csv'.format(site), header=True)


create_test()
#
#print col

#df = pd.DataFrame.from_dict(map(dict,df_list))
# for site in valid_sites:
# 	df = get_questions_and_tags(site, n/50)
# 	df = df.iloc[:,0]
# 	df.to_csv('{}_test.csv'.format(site), header=True)


print "--- n = {}, t = {} seconds ---".format(n, (time.time() - start_time))




