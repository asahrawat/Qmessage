from stackapi import StackAPI
import json
from flask import Flask, request
from twilio.twiml.messaging_response import Message, MessagingResponse
import time
import threading
from user import User
import time
import requests
from stackoverflow import post_question, find_similar
from twilio.rest import Client

'''
Heroku DB Example:
https://github.com/sahildiwan/flask-postgres-heroku/blob/master/app.py
'''

app = Flask(__name__)


TWILIO = '' ### redacted
MAX_SIZE = 1550
PHONES = {}

threadStarted = False

def wakeup_dyno():
	while True:
		r = requests.get(url = 'https://qmessage.herokuapp.com')
		print('waking up {}'.format(r)) 
		time.sleep(25*60)

@app.route('/', methods=['GET'])
def hello():
	message = '<p>Welcome to Qmessage, the messaging service where you can have your questions answered by real people!</p><p>Due to Free-Trial constraints, we have to add your number to our Twilio account before using the service, so, if you would like to use Qmessage, please ask Jorge (+14014404869) to add your number. If your number has already been added, then welcome back!</p><p>To use Qmessage, simply text anything to {}, and follow the instructions from there.</p>'.format(TWILIO)
	return message

@app.route('/sms', methods=['POST', 'GET'])
def sms():
	global threadStarted

	if not threadStarted:
		t = threading.Thread(target = thread_target)
		t.start()
		t1 = threading.Thread(target = wakeup_dyno)
		t1.start()
		threadStarted = True


	phone = request.form['From']

	if phone not in PHONES.keys():
		print("\nNew User: {}\n\n".format(phone))
		u = User(phone, TWILIO)
		PHONES[phone] = u
	else:
		u = PHONES[phone]

	response = u.process_message(request.form['Body'])
	u.previousMessage = response
	response = '.\n{}'.format(response)
	x = 0
	if len(response) > MAX_SIZE:
		r = response[MAX_SIZE]
		num = int(len(response) / MAX_SIZE) + 1
		for i in range(1, num):
			r = response[:MAX_SIZE]
			break_idx = r.rfind(' ') + 1
			if break_idx == 0: break_idx = MAX_SIZE
			r = response[:break_idx]
			response = response[break_idx:]
			send_message('({}/{})\n{}'.format(i, num, r), phone)
			x = i

		send_message('({}/{})\n{}'.format(x+1, num, response), phone)

	else: 
		resp = MessagingResponse()
		resp.message(response)
		return str(resp)



def thread_target():
	latest_post = 0
	while True:
		for user in PHONES.values():
			user.process_unanswered()
			latest_post = max(latest_post, user.latestPostTime)
			user.process_queue(latest_post)

		time.sleep(10)


def send_message(body, receiver):
		
		print('sending bytes from {} to {}'.format(TWILIO, receiver))
		account_sid = '' ### redacted
		auth_token = '' ### redacted
		
		client = Client(account_sid, auth_token)
		message = client.messages.create(
			body=body,
			from_=TWILIO,
			to=receiver
			)	


if __name__ == '__main__':
	
	app.debug = False
	app.run()
	
	'''
	u = User('+14014404869')
	PHONES['401'] = u
	while True:
		print('{}\n'.format('-'*40))
		message = input('---------\nYour message:\n')
		response = u.process_message(message)
		u.previousMessage = response
		print('--------------\nResponse:\n{}\n-----------'.format(response))
	'''

	
