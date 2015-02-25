#!/usr/bin/env python
#Implementation of IBM Model One Training

import itertools as it
import collections
import math

class ModelOne:
	def __init__(self, foreign_file, native_file, iterations=5, Verbose=False):
		"""
		foreign_file: path to the foreign language part of the bitext
		native_file: path to the native language part of the bitext
		iterations: number of EM iterations the user wishes to complete, default is 5
		Verbose: Set to True for debug information, default is False.

		After construction, access log-probability by 'myModel[native_word][foreign_word]'
		Just accessing 'myModel[native_word]' will return an OrderedDict that is sorted
		so that the best word is first.

		Similarly, a reverse dictionary will also be created which you can access by writing
		'myModel.reverseMap[foreign_word][native_word]'. 

		Caution: if the log-probability does not exist - it won't return float('-inf') so please
		check beforehand to see if something is in there. 
		"""
		#create necessary maps here
		self.foreign_lines = []
		self.native_lines = []
		self.foreign_vocab = set()
		self.native_vocab= set()
		self.probabilityMap = collections.defaultdict(lambda:collections.defaultdict(lambda: float('-inf')))
		self.reverseMap = collections.defaultdict(lambda: collections.defaultdict(lambda: float('-inf')))
		self.readFile(foreign_file, native_file)
		self.train(iterations, Verbose)

	def readFile(self, foreignName, nativeName):
		"""
		Loads in training data as list of lines - foreignName is the name of the file
		for the foreign text and nativeName is the name of the file for the native text
		"""
		with open(foreignName) as f:
			for line in f:
				words = line.strip().split()
				for word in words:
					self.foreign_vocab.add(word)
				self.foreign_lines.append(words)
		with open(nativeName) as n:
			for line in n:
				words = ["<NULL>"]
				words += line.strip().split()
				for word in words:
					self.native_vocab.add(word)
				self.native_lines.append(words)

	def train(self, iterations, Verbose=False):
		"""
		Trains the data and returns a map that can be indexed ["foreign word"]["native word"]
		that provides the log probablity of that word alignment
		"""
		iterations -= 1
		if Verbose:
			print "Iteration: ", 1

		# initialize t(f|e) uniformly / first iteration
		initMap = collections.defaultdict(lambda:collections.defaultdict(lambda: 0.0))
		for native_s, foreign_s in it.izip(self.native_lines, self.foreign_lines):
			for native_w in native_s:
				for foreign_w in foreign_s:
					initMap[native_w][foreign_w] += 1.0
		#normalize
		self._normalize(initMap)

		for iteration in xrange(iterations):
			if Verbose:
				print "Iteration: ", (iteration + 2)
			wordCounts = collections.defaultdict(lambda:collections.defaultdict(lambda: 0.0))
			nativeTotal = collections.defaultdict(lambda: 0.0)
			for foreign_s, native_s in it.izip(self.foreign_lines, self.native_lines):
				total_s = collections.defaultdict(lambda: 0.0)
				for foreign_w in foreign_s:
					for native_w in native_s:
						total_s[foreign_w] += initMap[native_w][foreign_w]
				for foreign_w in foreign_s:
					for native_w in native_s:
						wordCounts[native_w][foreign_w] += (initMap[native_w][foreign_w]/total_s[foreign_w])
						nativeTotal[native_w] += (initMap[native_w][foreign_w]/total_s[foreign_w])
			for native_w, n_value in nativeTotal.iteritems():
				for foreign_w, f_value in wordCounts[native_w].iteritems():
					initMap[native_w][foreign_w] = f_value / n_value

		if Verbose:
			print "Sorting and reversing dictionary..."
		for native_w, foreign_dict in initMap.iteritems():
			self.probabilityMap[native_w] = collections.OrderedDict(sorted(
				initMap[native_w].items(), key=lambda t:t[1], reverse=True), lambda: float('-inf'))
			for foreign_w, value in initMap[native_w].iteritems():
				self.reverseMap[foreign_w][native_w] = value

		if Verbose:
			print "Sorting reversed dictionary..."
		for foreign_w, native_dict in self.reverseMap.iteritems():
			self.reverseMap[foreign_w] = collections.OrderedDict(sorted(
				self.reverseMap[foreign_w].items(), key=lambda t:t[1], reverse=True), lambda: float('-inf'))


	def _normalize(self, initMap):
		"""
		Normalizes initMap so that the values of model["word"] sum to one
		"""
		for native_w, foreign_dict in initMap.iteritems():
			w_sum = math.log(sum(foreign_dict.values()))
			for foreign_w in foreign_dict.keys():
				initMap[native_w][foreign_w] = math.log(
					initMap[native_w][foreign_w]) - w_sum

	def _logProbAdd(self, a, b):
		"""
		Adds two log probabilities together!
		"""
		return -math.log(math.exp(-a) + math.exp(-b))

	def __getitem__(self, index):
		return self.probabilityMap[index]

######FOR TESTING PURPOSES ONLY########
def main():
	spanish_file = "../pa6/es-en/train/europarl-v7.es-en.es"
	english_file = "../pa6/es-en/train/europarl-v7.es-en.en"

	# spanish_file = "../pa6/test.es"
	# english_file = "../pa6/test.en"

	model = ModelOne(spanish_file, english_file, Verbose=True)

	print model["house"]["casa"]
	# for span_line, eng_line in it.izip(model.foreign_lines, model.native_lines):
	# 	print "Spanish: ", span_line
	# 	print "English: ", eng_line
	# print "Spanish Vocab: ", len(model.foreign_vocab)
	# print "English Vocab: ", len(model.native_vocab)

if __name__ == '__main__':
	main()
