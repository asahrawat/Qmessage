import pandas as pd
import numpy as np
from statistics import mean
import time
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer



COMMENT = 'title'

class Trainer:

	def __init__(self):

		self.valid_sites = ['math', 'politics', 'biology', 'cooking', 'history', 'cs']
		#self.valid_sites = ['history']
		self.data_set = 'small_training_data'
		#self.data_set = 'training_data'

		self.trained = {}


	def setup(self):
		for site in self.valid_sites:
			train = pd.read_csv('ml/{}/{}_data.csv'.format(self.data_set, site), error_bad_lines=False)
			self.train_setup(site, train)



	def train_setup(self, site, train):

		label_cols = list(train.columns[3:])
		vec = TfidfVectorizer(ngram_range=(1,2), 
					   min_df=3, max_df=0.9, strip_accents='unicode', use_idf=1,
					   smooth_idf=1, sublinear_tf=1 )
			
		trn_term_doc = vec.fit_transform(train[COMMENT])
		self.trained[site] = {
				'label_cols': label_cols,
				'train': train,
				'vec': vec,
				'trn_term_doc': trn_term_doc
			}


	def predict_tags_for_text(self, site, text):

		test = pd.DataFrame ([text], columns = [COMMENT])
			
		label_cols = self.trained[site]['label_cols']
		train = self.trained[site]['train']
		vec = self.trained[site]['vec']
		trn_term_doc = self.trained[site]['trn_term_doc']

		test_term_doc = vec.transform(test[COMMENT])
		x = trn_term_doc
		test_x = test_term_doc
		preds = np.zeros((len(test), len(label_cols)))

		def pr(y_i, y):
			p = x[y==y_i].sum(0)
			return (p+1) / ((y==y_i).sum()+1)


		def get_mdl(y):
			y = y.values
			r = np.log(pr(1,y) / pr(0,y))
			m = LogisticRegression(C=4, dual=True)
			x_nb = x.multiply(r)
			return m.fit(x_nb, y), r
			
		for i, j in enumerate(label_cols):
			m,r = get_mdl(train[j])
			preds[:,i] = m.predict_proba(test_x.multiply(r))[:,1]


		predictions = pd.concat([test, pd.DataFrame(preds, columns = label_cols)], axis=1)
		df = predictions.ix[:,1:]
		df = pd.DataFrame(df.columns.values[np.argsort(-df.values, axis=1)[:, :3]], 
	                  columns = ['1st Max','2nd Max','3rd Max']).reset_index()
	
		row = df.iloc[0, :]
		predicted_tags = [row['1st Max'], row['2nd Max'], row['3rd Max']]
		return predicted_tags





# t = Trainer()
# t.setup()


# question = 'Whats the run time complexity of the average decision tree?'
# topic = 'cs'

# start_time = time.time()
# print 'start'

# predicted_tags = t.predict_tags_for_text(topic, question)
# print 'Question: {}, tags: {}'.format(question, predicted_tags)

# print "--- t = {} seconds ---".format((time.time() - start_time))

