import json
from stackapi import StackAPI
from ordered_set import OrderedSet

APP_KEY = 'BAqwhDKJbi)Ifjom2U)VHQ(('
ACCESS_TOKEN = 'h3mAKlNtnfd(RQY8UUbUDg))'


SITES = {
	'math': 'maths',
	'statistics': 'statistics'
}

valid_sites = ['math', 'politics', 'biology', 'cooking', 'history', 'stackapps']


def get_questions_and_answers(topic, questionIds):
	try:
		if topic not in valid_sites:
			raise Exception('Unsupported topic')
		
		encoded = ';'.join(questionIds)
		method = 'questions/{}/answers'.format(encoded)
		SITE = StackAPI(topic, key=APP_KEY, access_token=ACCESS_TOKEN)
		
		response = SITE.fetch(method, filter='!-*jbN.OXKfDP')
		answers = response['items']
		curated = []
		for a in answers:
			rep = False
			#print a['title']
			#print a['question_id']
			#print '---------------'
			for i, c in enumerate(curated):
				if a['question_id'] == c['question_id']:
					curated[i]['answers'].append(a['body'])	
					rep = True
			if not rep:
				curated.append({'question_id': a['question_id'], 'question_title': a['title'], 'answers': [a['body']]})

		return curated
	except Exception as e:
		print e.message
		return []



def find_similar(topic, title, body, tags):

	print '{}, {}, {}, {}'.format(topic, title, body, tags)

	if topic not in valid_sites:
		raise Exception('Unsupported topic')
	
	method = 'search/advanced'
	SITE = StackAPI(topic, key=APP_KEY, access_token=ACCESS_TOKEN)
	
	similar = []
	similar += SITE.fetch(method, title=title, tags=';'.join(tags), answers=1, sort='votes')['items'] # title match and 1+ tags match
	similar += SITE.fetch(method, title=title, answers=1, sort='votes')['items'] # title match
	similar += SITE.fetch(method, body=title, tags=';'.join(tags), answers=1, sort='votes')['items'] # title in body and 1+ tags match
	similar += SITE.fetch(method, body=title, answers=1, sort='votes')['items'] # title in body
	
	ids = OrderedSet()
	for s in similar: 
		ids.add(str(s['question_id']))
	ids = list(ids)

	return get_questions_and_answers(topic, ids)



def post_question(topic, title, body, tags):
	if topic not in valid_sites:
		raise Exception('Unsupported topic')
	
	method = 'questions/add'
	SITE = StackAPI(topic, key=APP_KEY, access_token=ACCESS_TOKEN)
	
	#title = 'PLACEHOLDER - ' + title
	#tags.append('placeholder')
	#tags.append('app')
	response = SITE.send_data(method, title=title, body=body, tags=tags)
	return response




'''
# Write to DB
def store_new_question(questionId, phoneNumber):
	answered = False
	DB.append({
		'questionId': str(questionId),
		'phone': phoneNumber,
		'isAnswered': False
		})
	print 'Storing question {}, by {} - answered? {}'.format(questionId, phoneNumber, answered)





def get_questions(topic, questionIds):
	encoded = ';'.join(questionIds)
	method = 'questions/{}'.format(encoded)
	SITE = StackAPI(topic, key=APP_KEY, access_token=ACCESS_TOKEN)
	response = SITE.fetch(method)
	print json.dumps(response)
	return response


def pull_questions():
	questionIds = [elem['questionId'] for elem in DB if not elem['isAnswered']]
	return get_questions(questionIds)


def get_questions_from_user(userId):
	method = 'users/{}/questions'.format(userId)
	response = SITE.fetch(method)
	return response['items']
'''









