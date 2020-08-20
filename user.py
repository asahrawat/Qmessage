## Final Version ## NEWEST EDIT


import html2text
import time
import json
from stackoverflow import post_question, find_similar, get_questions_and_answers
from ml.trainer import Trainer
from twilio.rest import Client


def htmlToText(text):
	try:
		html = str(html2text.html2text(text))
		return html
	except Exception as e:
		return "NA"

class User:

	def __init__(self, phone, serverPhone=''): ### redacted

		self.trainer = Trainer()
		self.trainer.setup()
		self.maxList = 5
		self.previousMessage = ""

		self.phone = phone
		self.serverPhone = serverPhone
		self.history = [] #List of all previous groups of interactions DELETE
		self.queueToAsk = []
		self.unansweredQuestionTuples = []
		self.answeredQuestionTuples = []

		self.forward_seen = 0
		self.current_forward_questions = []
		self.toForwardId = None

		self.latestPostTime = 0
		self.questionToAsk = None

		self.current = None
		
		self.title = ""
		self.topic = None
		self.tags = []
		
		self.similarMessage = ""
		self.similar_questions = []
		self.similarCurrent = ""

		self.acceptedTopics = ["math", "politics", "biology", "cooking", "history", "cs"]

		self.examples = {
			'math': 'Why does the monotone convergence theorem not apply on Riemann integrals?',
			'politics': 'What will the consequences of Brexit be on EURONEXT?',
			'biology': 'How do homologous pairs find each other?',
			'cooking': 'What happens if I use vegetable oil in a cake?',
			'history': 'How Did the Mongol Empire Get So Big?',
			'cs': 'Proving that the conversion from CNF to DNF is NP-Hard'
		}

		self.exampleBodies = {
			'math': "I had just learned in measure theory class about the monotone convergence theorem in this version:\nFor every monotonically increasing series of functions fn from measurable space X to [0, infinity],\n\nI tried to find out why this theorem apply only for a Lebesgue integral, but I didn't find a counter example for Riemann integrals, so I would appreciate your help.\n(I guess that f might not be integrable in some cases, but I want a concrete example.)",
			'politics': "I've heard that Euronext (which is related to financial products of France, Netherland,...) was physically located near London.\nSuppose that a 'hard' brexit happens. Will be any consequence about the future location of Euronext (even partially).\n\nAnd if it's the case: Will be consequences on the connectivity of the european market place to the other ones?",
			'biology': "If I'm not mistaken the only time homologous pairs of chromosomes need to find each other is during gamete formation in preparation for crossover recombination. How do they find each other?",
			'cooking': "I want to bake a cake out of baking mix bought at a shop. The mix already contains flour, baking soda, vanillin, other minor components. The manual says I need to add butter.\n\nI'd like to use vegetable oil instead of butter - most likely sunflower seed oil. Is that a good idea? Should I expect any problems? Will the result likely be a decent cake or something to just throw away?",
			'history': "Undoubtedly, the largest empire in the existence of human history was the Mongol Empire, once a hodgepodge of warring nomadic tribes from Central Asia before banding together under the banner of Temujin, better known as Genghis Khan.\nBut what was the key to the Mongol Empire's size? Was the horse, the most ideal creature to use for long-distance travel, the exclusive reason? Or were there other factors involved?How Did the Mongol Empire Get So Big?",
			'cs': "How can I prove that the conversion from CNF to DNF is NP-Hard?\nI'm not asking for an answer, just some suggestions about how to go about proving it."
		}

		
		self.responses = {
						'helloK': '\nWelcome to Qmessage, the messaging service where you can have your questions answered by real people!\n\nReply 1 (ONE) to ask a new question.\nReply 2 (TWO) to forward a previously asked question (and answer) to another contact.\nReply 3 (THREE) for help.',
						'askK': "\nYou have selected the topic '{}'.\n\nReply with the title of your question (short and descriptive sentence with appropriate vocabulary).\nReply EXAMPLE to see an example question title.\nReply EXIT to exit.",
						'askJ': "\nReply with the topic that corresponds to your question, from the following list: math, politics, biology, cooking, history, or cs (computer science).\nReply EXIT to exit.",
						'exampleAsk':"\nA title is a preview or summary of your question, such as '{}'\n",
						'askYes':"\nThe title of your question is '{}'.\n\nReply with a descriptive body for your question, so we can post it to the forum and wait for someone to answer it.\nReply EXAMPLE to see an example.\nReply EXIT to exit.",
						'askNo': "\nOk. Have a good day! Goodbye for now.",
						'askBrowsing':"\nReply 1 (ONE) to rephrase your question under the same topic.\nReply 2 (TWO) to ask a completely new question.\nReply 3 (THREE) in order to post your current question to the forum.\nReply EXIT to exit.",

						'forwardK': '\nHere are the titles of your most recently answered questions.\n\nReply with the corresponding question number you wish to forward.\nReply MORE to see older questions.\nReply EXIT to exit.\n\n',
						'helpK': '\nQmessage is an SMS-based service that allows you to post questions on a platform where thousands of people can look at and answer them. Any inquiry you have, on topics ranging from biology to cooking, may be answered! If we find similar questions to yours that have already been answered, we forward them immediately; otherwise, we post your question and wait until someone answers it. Keep in mind that this may take a few hours, depending on the relevance of the topic.\nWe also support question sharing, so that you can send your past questions (with answers) to your friends and family.\nTo use the service, simply follow the instructions at each step. Thank you for using Qmessage!',
						'errorK': '\nI do not understand your message. Please try another response.\n',
						'exampleQ': "\nHere is an example of a complete question:\n\nTitle:\n{}\n\nBody:\n{}\n\n",
						'confirmQ': '\nYour question has been sent in! We will notify you when we receive a response. Goodbye for now.',
						'forwNum': '\nYou have selected the following question: {}.\n\nReply with the phone number of the person you would like to forward this question and answer to, including the international area code (e.g. +16034445678).\nReply EXIT to exit.',
						'similarQ': '\nWe found some questions similar to yours! Below are their titles.\n\nReply with the corresponding question number to look at the answer.\nReply NONE if none of them seem relevant, and we can browse other questions or post yours and wait for an answer.\nReply EXIT to exit.',
						'confirmSimilar': "\nBelow is the top-ranked answer to the question\n{}\nReply 1 (ONE) if this was the answer you were looking for.\nReply 2 (TWO) to return to the list of similar questions.\nReply EXIT to exit.\n",
						'confirmSimilarExit': "\nGreat! Have a nice day! Goodbye for now.",
						'errorQ': '\nThe platform did not accept your question. This is their message:',
						'unansweredQ': '\nHi! Someone has answered the following question:\n\n',
						'noMoreForwards': '\nAt the moment, you have no more answered questions available to forward.',
						'confirmForward': '\nThank you! We have forwarded the information to your contact. Goodbye for now.'
						}


	def next_state(self, message):

		print('NEW LOOP. State: {}, message: {}\n'.format(self.current, message))
		
		# GENERIC EXIT
		if message.upper() == "EXIT" or message.upper() == "EXIT ":
			return ('exit', self.responses['askNo'])
		

		if self.current is None or self.current == 'exit': #or self.current is 'error':
			self.topic = None
			self.forward_seen = 0
			self.current_forward_questions = []
			self.toForwardId = None
			return ('hello', self.responses['helloK'])


		elif self.current == 'hello':
			#ASK 
			if '1' == message or 'ONE' in message.upper():
				return ('askTopic', self.responses['askJ'])
			#FORWARD
			elif '2' == message or 'TWO' in message.upper():
				questions = self.generate_forward_options()
				if len(questions) > 0:
					self.current_forward_questions = questions
					message = self.responses['forwardK']
					for i, q in enumerate(questions):
						message += '{}. {}'.format(i+1, htmlToText(q['question_title']))
					return ('forward', message)
				else:
					self.forward_seen = 0
					return ('hello', self.responses['noMoreForwards'] + '\n' + self.responses['helloK'])
			#HELP
			elif '3' == message or 'THREE' in message.upper():
				return ('hello', self.responses['helpK'] + '\n' + self.responses['helloK'])


		elif self.current == 'askTopic':
			if message.lower() in self.acceptedTopics:
				self.topic = message.lower()
				return ('ask', self.responses['askK'].format(self.topic))


		elif self.current == 'ask':
			if message.upper() == "EXAMPLE" or message.upper() == "EXAMPLE ":
				return ('ask', self.responses['exampleAsk'].format(self.examples[self.topic]) + self.responses['askK'].format(self.topic))
			elif len(message) < 15:
				return ('ask', '\nQuestion titles must contain at least 15 characters.\n' + self.responses['askK'].format(self.topic))
			else:
				self.title = message
				try:
					# Actually found some similar questions
					self.tags = self.predict_tags_for_text(self.title)
					similar = self.similar_qs(self.title, self.tags)

					#return ('similar', similar)
					similar = similar[:5]

					if len(similar) > 0:
						self.similar = similar
						message = self.responses['similarQ'] + '\n\n'

						for i, s in enumerate(similar):
							message += '{}. {}'.format(i + 1, htmlToText(s['question_title']))
					
						self.similarMessage = message

						return ('similar', self.similarMessage) #we're only doing one set of questions for this version. Additional similar questions coming in v2.

					# No similar questions
					else:
						return ('askPath', "\nWe found no previously asked questions that resemble yours.\n" + self.responses["askBrowsing"])

				except Exception as e:
					return ('ask', '{}\n{}\n{}\n'.format(self.responses['errorQ'], str(e.args[-1]), self.responses['askK'].format(self.topic)))


		#ALTERNATIVE
		elif self.current == 'askPath':
			# REPHRASE QUESTION
			if "ONE" in message.upper() or "1" == message:
				return ('ask', self.responses['askK'].format(self.topic))
			# POST QUESTION
			elif "TWO" in message.upper() or "2" == message:
				return ('askTopic', self.responses['askJ'])
							
			elif "THREE" in message.upper() or "3" == message:
				return ('askScreen', self.responses['askYes'].format(self.title))



		elif self.current == 'askScreen':

			if "EXAMPLE" == message.upper():
				return ('askScreen', self.responses['exampleQ'].format(self.examples[self.topic], self.exampleBodies[self.topic]) + self.responses['askYes'].format(self.title))
			elif len(message) < 30:
				return ('askScreen', '\nQuestion bodies must contain at least 30 characters.\n' + self.responses['askYes'].format(self.title))
			else:
				body = message
				self.body = body
				try:
					self.ask_question(self.topic, self.title, self.body, self.tags)
					return ("exit", self.responses["confirmQ"])
				except Exception as e:
					return ('askScreen', '{}\n{}\n{}\n'.format(self.responses['errorQ'], str(e.args[-1]), self.responses['askYes'].format(self.title)))




		elif self.current == 'forward':
			#FORWARD SELECTED
			if message.isdigit():
				i = int(message) - 1
				##print 'In forwarding, with digit'
				if i < len(self.current_forward_questions) and i >= 0:
					self.toForward = self.current_forward_questions[i]
					self.forward_seen = 0
					return ('provideNum', self.responses['forwNum'].format(self.toForward['question_title']))
			#MORE FORWARD
			elif 'MORE' in message.upper():
				questions = self.generate_forward_options()
				if len(questions) > 0:
					self.current_forward_questions = questions
					message = self.responses['forwardK']
					for i, q in enumerate(questions):
						message += '{}. {}'.format(i+1, htmlToText(q['question_title']))

					return ('forward', message)
				else:
					self.forward_seen = 0
					return ('hello', self.responses['noMoreForwards'] + '\n' + self.responses['helloK'])

			

		elif self.current == 'provideNum':
			q = self.toForward
			body = 'Hi, this is Qmessage! User {} has asked to forward you the following question and answer:\n\n'.format(self.phone)
			body += 'Question Title: {}\n{}'.format(htmlToText(q['question_title']), htmlToText(q['answers'][0]))
			try:				
				self.send_message(body, message)
				return ('exit', self.responses['confirmForward'])
			except Exception as e:
				return ('provideNum', '\nWe were unable to forward the question. Please make sure that the phone number is valid.\n{}'.format(self.responses['forwNum'].format(self.toForward['question_title'])))
			self.toForward = None
			

		elif self.current == 'similar':
			if message.isdigit():
				i = int(message) - 1
				if i < len(self.similar) and i >= 0:
					s = self.similar[i]
					self.similarCurrent = '\n{}\n{}'.format(htmlToText(s['question_title']), htmlToText(s['answers'][0]))
					message = self.responses['confirmSimilar'].format(self.similarCurrent)
					return ('confirmSim', message)
				else:
					return ('similar', "Please enter a valid index\n\n" + self.similarMessage)

			elif 'NONE' in message.upper():
				# ALTERNATIVE
				return ('askPath', self.responses["askBrowsing"])


		elif self.current == 'confirmSim':
			if message.upper() == "ONE" or message == "1":
				self.similar = []
				self.similarCurrent = ""
				return ('exit', self.responses['confirmSimilarExit'])
			elif message.upper() == "TWO" or message == "2":
				return ('similar', self.similarMessage)
			

		print("Previous: {}".format(self.previousMessage))
		return (self.current, self.responses['errorK'] + self.previousMessage.replace(self.responses['errorK'], ""))



	def generate_forward_options(self):

		print('in generate. answered: {}, seen: {}'.format(len(self.answeredQuestionTuples), self.forward_seen))
		if self.forward_seen >= len(self.answeredQuestionTuples): 
			return []

		next_batch = self.answeredQuestionTuples[self.forward_seen:][:self.maxList]
		print(next_batch)
		forwards = []
		for tup in next_batch: forwards += get_questions_and_answers(tup[0], [tup[1]])
		self.forward_seen += len(next_batch)
		return forwards


	def process_message(self, message):
		self.history.append(message)
		curr_state, to_usr = self.next_state(message)
		self.current = curr_state
		return to_usr
		

	def process_unanswered(self):
		if len(self.unansweredQuestionTuples) > 0:
			print('processing unanswered: {}'.format(self.unansweredQuestionTuples))
			for topic, qid in self.unansweredQuestionTuples:
				questions = get_questions_and_answers(topic, [qid])
				if len(questions) > 0:
					q = questions[0]
					new_tuples = [i for i in self.unansweredQuestionTuples if i[1] != qid] 
					self.unansweredQuestionTuples = new_tuples

					message = self.responses['unansweredQ']
					message += 'Question Title: {}'.format(htmlToText(q['question_title']))
					message += 'Answers:\n'
					for i, a in enumerate(q['answers']):
						message += '{}. {}\n'.format(i+1, htmlToText(a))

					self.answeredQuestionTuples.append((topic, qid))
					self.send_message(message)

			print('after unanswered: {}'.format(self.unansweredQuestionTuples))


	def process_queue(self, latestPostTime):
		now = int(time.time())
		print('latestPostTime: {}'.format(latestPostTime))
		if (now - latestPostTime) / 60 > 40 and len(self.queueToAsk) > 0:
			q = self.queueToAsk.pop(0)
			try:
				self.ask_question(q[0], q[1], q[2], q[3])
			except:
				pass


	def send_message(self, body, receiver=None):
		if receiver is None:
			receiver = self.phone

		print('sending {} bytes from {} to {}'.format(len(body), self.serverPhone, receiver))
		
		account_sid = '' ### redacted
		auth_token = '' ### redacted
		client = Client(account_sid, auth_token)

		body = (body[:1550] + '...') if len(body) > 1550 else body
		body = '.\n{}'.format(body)

		message = client.messages.create(
			body=body,
			from_=self.serverPhone,
			to=receiver
			)	
		

	def ask_question(self, topic, title, body, tags):
		try:		
			qid = post_question(topic, title, body, tags)
			print('Adding question to unanswered questions: {}'.format(qid))
			self.unansweredQuestionTuples.append((self.topic, str(qid)))
			self.latestPostTime = int(time.time())
		except Exception as e:
			print(str(e.args[-1]))
			if 'You can only post once every 40 minutes.' == str(e.args[-1]):
				print('Adding question to pending queue!!!')
				self.queueToAsk.append((topic, title, body, tags))
			else:
				message = str(e.args[-1]).replace("You can only post once every 40 minutes.","");
				raise Exception(message)


	def predict_tags_for_text(self, question):
		try:
			tags = self.trainer.predict_tags_for_text(self.topic, question) ###UNCOMMENT FOR FINAL VERSION
			return tags
		except Exception as e:
			print(str(e.args[-1]))
			return []


	def similar_qs(self, title, tags):
		try:
			similar = find_similar(self.topic, title, tags)
			asciiSimilar = []

			for s in similar:
				if htmlToText(s['question_title']) != 'NA' and htmlToText(s['answers'][0]) != 'NA':
					asciiSimilar.append(s)

			return asciiSimilar
		except Exception as e:
			print(str(e.args[-1]))
			return []
						



						

