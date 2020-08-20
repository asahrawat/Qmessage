import json
from stackapi import StackAPI
from ordered_set import OrderedSet

APP_KEY = '' ### redacted
ACCESS_TOKEN = '' ### redacted

valid_sites = ['math', 'politics', 'biology', 'cooking', 'history', 'cs']


def get_questions_and_answers(topic, questionIds):
	if len(questionIds) == 0: return []
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
			for i, c in enumerate(curated):
				if a['question_id'] == c['question_id']:
					curated[i]['answers'].append(a['body'])	
					rep = True
			if not rep:
				curated.append({'question_id': a['question_id'], 'question_title': a['title'], 'answers': [a['body']]})
		print(len(curated))
		return curated
	except Exception as e:
		print(e.message)
		return []



def find_similar(topic, title, tags):

	print('DEBUG IN FIND SIMILAR: {}, {}, {}\n'.format(topic, title, tags))

	if topic not in valid_sites:
		raise Exception('Unsupported topic')
	
	method = 'search/advanced'
	SITE = StackAPI(topic, key=APP_KEY, access_token=ACCESS_TOKEN)
	
	similar = []
	similar += SITE.fetch(method, q=title, tags=';'.join(tags), answers=1, sort='votes')['items'] # title match and 1+ tags match
	similar += SITE.fetch(method, q=title, answers=1, store_new_question='votes')['items'] # title match
	#similar += SITE.fetch(method, tags=';'.join(tags), answers=1, sort='votes')['items'] # 1+ tags match
	
	ids = OrderedSet()
	for s in similar: 
		ids.add(str(s['question_id']))
	ids = list(ids)[:15] # Top 15

	print('{} SIMILAR FOUND\n'.format(len(ids)))
	
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
	try:
		qid = response['question_id']
	except: 
		print(json.dumps(response))
		qid = response['items'][0]['question_id']
	return qid






