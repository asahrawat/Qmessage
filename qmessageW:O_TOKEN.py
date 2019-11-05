from stackapi import StackAPI
import json
from flask import Flask, request
from twilio.twiml.messaging_response import Message, MessagingResponse
import time
import threading
from user import User
from stackoverflow import post_question, find_similar

'''
Twilio:
+18723954993
Heroku DB Example:
https://github.com/sahildiwan/flask-postgres-heroku/blob/master/app.py
'''

app = Flask(__name__)

TWILIO = ''

PHONES = {}
APP_KEY = ''
ACCESS_TOKEN = ''
#SITE = StackAPI('stackapps', key=APP_KEY, access_token=ACCESS_TOKEN)

@app.route('/sms', methods=['POST', 'GET'])
def sms():
	print 'GOT YOU'
	phone = request.form['From']

	if phone not in PHONES.keys():
		print "\nNew User: {}\n\n".format(phone)
		u = User(phone, TWILIO)
		PHONES[phone] = u
	else:
		print "\nOld User: {}\n\n".format(phone)
		u = PHONES[phone]

	response = u.process_message(request.form['Body'])
		
	resp = MessagingResponse()
	resp.message(response)
	return str(resp)


def thread_target():
	latest_post = 0
	while True:
		print '...\n'
		for user in PHONES.values():
			user.process_unanswered()
			user.process_queue(latest_post)
			latest_post = max(latest_post, user.latestPostTime)

		time.sleep(5)


if __name__ == '__main__':

	t = threading.Thread(target = thread_target)
	t.start()
	#app.debug = False
	app.run()

	

	
	
	'''

	while True:
		print '{}\n'.format('-'*40)
		c = raw_input('command:')
		if c == 'queue':
			u.process_queue(u.latestPostTime)
		elif c == 'unanswered':
			u.process_unanswered()
		else:
			response = u.process_message(c)
			print 'Response:\n{}'.format(response)


	while True:
		print '{}\n'.format('-'*40)
		message = raw_input('Your message:\n')
		response = u.process_message(message)
		print 'Response:\n{}'.format(response)
	


	accounts = ['math', 'politics', 'biology', 'cooking', 'history', 'stackapps']
	accounts = ['math']
	while True:
		print '{}\n'.format('-'*40)
		m = raw_input('Method (post or get):\n')
		if m == 'post':
			s = 'math'
			t = 'how do you solve a system of equations?'
			b = 'I have 2 formulas: y = x + 2 and x = 87. How do I find y?'
			ts = ['system of equations', 'unknown variables']
			#resp = post_question(s, t, b, ts)
			resp = find_similar(s, t, b, ts)
			print json.dumps(resp)
	'''
	


	#app.run()




	'''
	title = 'title'
	body = 'body'
	phoneNumber = 4014404869
	post_question('', '', phoneNumber)

	for i in range(3):
		x = pull_questions()
		print json.dumps(x)
		print '-----\n\n'
		time.sleep(2)
	'''

#response = SITE.send_data('questions/add', 
#	title='PLACEHOLDER - Finding population mean from sample statistics', 
#	body='I know that I can use a Z statistic or t-statistic, but I do not know how to do it if I am only given a sample mean. (Testing app)', 
#	tags='placeholder;app')


#print(response)
#print(comments)

#flag = SITE.send_data('comments/123/flags/add', option_id=option_id)
#print(flag)

#https://api.stackexchange.com/2.2/users/%7B%7D/1;6;3;1;8/ ?pagesize=100&page=1&filter=default&key=BAqwhDKJbi%29Ifjom2U%29VHQ%28%28&access_token=h3mAKlNtnfd%28RQY8UUbUDg%29%29&site=cooking


#https://api.stackexchange.com/2.2/users%2F%7B%5B16318%5D%7D?pagesize=100&page=1&filter=default&key=BAqwhDKJbi%29Ifjom2U%29VHQ%28%28&access_token=h3mAKlNtnfd%28RQY8UUbUDg%29%29&site=cooking