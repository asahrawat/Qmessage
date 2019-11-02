import html2text
import time
import json
from stackoverflow import post_question, find_similar, get_questions_and_answers
from twilio.rest import Client

class User:

	def __init__(self, phone, serverPhone):
		self.phone = phone
		self.serverPhone = serverPhone
		self.history = [] #List of all previous groups of interactions DELETE
		self.queueToAsk = []
		self.unansweredQuestionIds = []
		self.latestPostTime = 0
		self.questionToAsk = None

		self.current = None
		self.toForward = ""  #holds question and answer that user wants to forward
		self.topic = "math"
		self.tags = ['linear-algebra', 'systems-of-equations']

		self.similar_questions = []
		
		self.responses = {
						'helloK': '\nWelcome to Qmessage, the messaging service where you can have your questions answered by real people.\nReply ONE to ask a new question,\nReply TWO to forward a previously asked question (and answer) to another contact\nReply THREE for help',
						'askK': '\nPlease ask a question. Keep your question in the format of "[Title]; [Question]".\nFor an example, reply EXAMPLE.\nPlease keep your question appropriate and make sure your title matches your question."',
						'forwardK': '\nForwarding: Here are a list of questions you have asked along with their answers. Reply the number corresponding to the question in order to forward. Reply FIVE for more questions.',
						'helpK': '\nThis is a help message.', #TODO
						'errorK': '\nI do not understand your message. Please try another response.',
						'exampleQ': '\nHere is an example of a question:\nHow do you solve a system of equations?; I have 2 formulas: y = x + 2 and x = 87. How do I find y?',
						'confirmQ': '\nYour question has been sent in! We will notify you when we receive a response.',
						'forwNum': '\nPlease provide the phone number of the person you would like to forward this question and answer to. Please include the international area code. Ex: +16034445678.',
						'similarQ': '\nWe found some similar questions to yours. If you would like to see the answers to one of these questions, please reply with the corresponding number. Otherwise, please reply NONE and we will go ahead and post your question',
						'confirmSimilar': "\nGreat! Here are the answer(s) to the question:\n",
						'errorQ': '\nhTe platform did not accept the question. This is their message:\n',
						'unansweredQ': '\nHey! Someone has answered your previously asked questions!\n'
			
						}


	def next_state(self, message):
		if self.current is None: #or self.current is 'error':
			return ('hello', self.responses['helloK'])


		elif self.current == 'hello':
			if '1' == message or 'ONE' in message.upper():
				return ('ask', self.responses['askK'])
			elif '2' == message or 'TWO' in message.upper():
				return ('forward', self.responses['forwardK'] + '\n' + 'Forward List 1')
			elif '3' == message or 'THREE' in message.upper():
				return ('hello', self.responses['helpK'])
			else:
				return ('hello', self.responses['errorK'] + '\n' + self.responses['helloK'])


		elif self.current == 'ask':
			if message.upper() == "EXAMPLE":
				return ('ask', self.responses['exampleQ'] + "\n" + self.responses['askK'])
			elif ";" in message:
				title, question = message.split(";",)   ###CHECK THIS
				
				try:
					# Actually found some similar questions
					similar = find_similar(self.topic, title, question, self.tags)
					similar = similar[:5]
					if len(similar) > 0:
						self.similar = similar
						message = self.responses['similarQ'] + '\n'
						for i, s in enumerate(similar):
							message += '{}. {}\n'.format(i, html2text.html2text(s['question_title']))
					
						self.questionToAsk = (self.topic, title, question, self.tags)
						return ('similar', message) #we're only doing one set of questions for this version. Additional similar questions coming in v2.

					# No similar questions
					else:
						self.ask_question(self.topic, title, question, self.tags)
						return ('exit', self.responses['confirmQ'])

				except Exception as e:
					return ('ask', '{}\n{}\n\n{}\n'.format(self.responses['errorQ'], e.message, self.responses['askK']))
			else:
				return ('ask', self.responses['errorK'] + '\n' + self.responses['askK'])


		elif self.current == 'forward':
			if '1' in message or 'ONE' in message.upper():
				#self.toForward = questions[0] assume there is a list of questions pulled from API and it is in a list called 
				return ('provideNum', self.responses['forwNum'])
			elif '2' in message or 'TWO' in message.upper():
				#self.toForward = questions[1]
				return ('provideNum', self.responses['forwNum'])
			elif '3' in message or 'THREE' in message.upper():
				#self.toForward = questions[2] 
				return ('provideNum', self.responses['forwNum'])
			elif '4' in message or 'FOUR' in message.upper():
				#self.toForward = questions[3] Figure out how this would work for 'Forward List 2' #TODO
				return ('provideNum', self.responses['forwNum'])
			elif '5' in message or 'FIVE' in message.upper():
				return ('forward', self.responses['forwardK'] + '\n' + 'Forward List 2') #TODO next forward list
			else:
				#error message
				return ('forward', self.responses['errorK'] + '\n' + self.responses['forwardK'] + '\n' + 'Forward List 1') #TODO forward list


		elif self.current == 'provideNum':
			#make API call to forward question
			#pass self.toForward
			#also exit state
			return ('exit', self.reponses['errorK'] + '\n' + self.responses['confirmQ'])


		elif self.current == 'similar':
			if message.isdigit():
				i = int(message)
				if i < len(self.similar):
					s = self.similar[i]
					message = self.responses['confirmSimilar']
					answers = s['answers'][:3] # up to 3 answers
					for i, a in enumerate(answers):
						message += '{}. {}\n'.format(i, html2text.html2text(a))
					
					message += '\nHave a great day!'
					return ('exit', message)

			elif 'NONE' in message.upper():
				try:
					self.ask_question(self.questionToAsk[0], self.questionToAsk[1], self.questionToAsk[2], self.questionToAsk[3])
					self.questionToAsk = None
					return ('exit', self.responses['confirmQ'])
				except Exception as e:
					return ('ask', self.responses['errorQ'] + self.responses['askK'])

		return ('hello', self.responses['errorK'] + '\n' + self.responses['helloK'])


	def process_message(self, message):
		self.history.append(message)
		#self.prev = self.current
		curr_state, to_usr = self.next_state(message)
		self.current = curr_state

		return to_usr
		#return self.responses[self.current]


	def process_unanswered(self):
		if len(self.unansweredQuestionIds) > 0:
			questions = get_questions_and_answers(self.topic, self.unansweredQuestionIds)
			message = self.responses['unansweredQ']
			for q in questions:
				self.unansweredQuestionIds.remove(str(q['question_id']))

				message += 'Question Title: {}\n'.format(html2text.html2text(q['question_title']))
				message += 'Answers:\n'
				for i, a in enumerate(q['answers']):
					message += '{}. {}\n'.format(i, html2text.html2text(a))

			if len(questions) > 0:
				self.send_message(message)

	def process_queue(self, latestPostTime):
		now = int(time.time())
		if (now - latestPostTime) / 60 > 40 and len(self.queueToAsk) > 0:
			q = self.queueToAsk.pop(0)
			try:
				self.ask_question(q[0], q[1], q[2], q[3])
			except:
				pass

	def send_message(self, body):
		account_sid = 'AC9f18826969a649e1f2f1163d0da5ab53'
		auth_token = '159b0ab8c8f8a7b2cdd9c709cd7e3694'
		client = Client(account_sid, auth_token)

		message = client.messages.create(
			body=body,
			from_=self.serverPhone,
			to=self.phone
			)
		print 'sent!'

	def ask_question(self, topic, title, body, tags):
		try:		
			qid = post_question(topic, title, body, tags)
			print 'Adding question to unanswered questions!!!'
			self.unansweredQuestionIds.append(qid)
			self.latestPostTime = int(time.time())
		except Exception as e:
			print e.message
			if 'You can only post once every 40 minutes.' == e.message:
				print 'Adding question to pending queue!!!'
				self.queueToAsk.append((topic, title, body, tags))
			else:
				raise Exception(e.message)
						

