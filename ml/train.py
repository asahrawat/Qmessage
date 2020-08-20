import pandas as pd, numpy as np
from statistics import mean
import time
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer



COMMENT = 'title'

start_time = time.time()



def train_machine(train, test):
	def pr(y_i, y):
		p = x[y==y_i].sum(0)
		return (p+1) / ((y==y_i).sum()+1)

	def get_mdl(y):
		y = y.values
		r = np.log(pr(1,y) / pr(0,y))
		m = LogisticRegression(C=4, dual=True)
		x_nb = x.multiply(r)
		return m.fit(x_nb, y), r


	label_cols = list(train.columns[3:])
	print '{} tags'.format(len(label_cols))

	vec = TfidfVectorizer(ngram_range=(1,2), 
				   min_df=3, max_df=0.9, strip_accents='unicode', use_idf=1,
				   smooth_idf=1, sublinear_tf=1 )
	trn_term_doc = vec.fit_transform(train[COMMENT])
	test_term_doc = vec.transform(test[COMMENT])
	x = trn_term_doc
	test_x = test_term_doc

	preds = np.zeros((len(test), len(label_cols)))

	for i, j in enumerate(label_cols):
		m,r = get_mdl(train[j])
		preds[:,i] = m.predict_proba(test_x.multiply(r))[:,1]


	submission = pd.concat([test, pd.DataFrame(preds, columns = label_cols)], axis=1)

	return submission



def evaluate_model(test, submission):
	df = submission.ix[:,4:]
	df = pd.DataFrame(df.columns.values[np.argsort(-df.values, axis=1)[:, :3]], 
	                  columns = ['1st Max','2nd Max','3rd Max']).reset_index()
	df = df.ix[:,1:]
	df = pd.concat([test, df], axis=1)
	
	overlaps = []
	for index, row in df.iterrows():
		og = row['tags']
		ogs = og.split(',')
		prs = [row['1st Max'], row['2nd Max'], row['3rd Max']]

		overlap = set(ogs) & set(prs)
		pOver = len(list(overlap)) / float(min(len(ogs), len(prs)))
		overlaps.append(pOver)

	return (df, overlaps)
	

def run():
	valid_sites = ['math', 'politics', 'biology', 'cooking', 'history', 'cs']

	for site in valid_sites:
		train = pd.read_csv('training_data/{}_data.csv'.format(site), error_bad_lines=False)
		test = pd.read_csv('test_data/{}_test.csv'.format(site), error_bad_lines=False)

		submission = train_machine(train, test)

		prediction, overlaps = evaluate_model(test, submission)
		prediction.to_csv('predictions/{}_prediction.csv'.format(site), index=False)

		atLeast = np.count_nonzero(overlaps) / float(len(overlaps))

		print 'SITE: {}, {} training values, {} testing values'.format(site, len(train.index), len(test.index))
		print 'OVERLAPS --> min: {}, max: {}, mean: {}, at-least-1: {}\n\n'.format(min(overlaps), max(overlaps), mean(overlaps), atLeast)


run()
print "--- t = {} seconds ---".format((time.time() - start_time))




