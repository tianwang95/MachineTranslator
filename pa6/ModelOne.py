#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Implementation of IBM Model One Training
#Tian Wang, Bogac Kerem Goksel, Russell Kaplan, Duc Nguyen

import itertools as it
import collections
import math
import cPickle as pickle
import re

def getDict():
	return collections.Counter()

class ModelOne:
	def __init__(self, foreign_file=None, native_file=None, loadFile=None, iterations=5, Verbose=False):
		"""
		To use: In the import, you MUST also import getDict:
			from ModelOne import ModelOne, getDict'

		To load from file do:
			MyModel = ModelOne(loadFile="save.model")

		To save to a file:
			MyModel.saveToFile("save.model")

		foreign_file: path to the foreign language part of the bitext - default is None

		native_file: path to the native language part of the bitext - default is None
		
		iterations: number of EM iterations the user wishes to complete, default is 5
		Verbose: Set to True for debug information, default is False.

		Example:
			MyModel = ModelOne("../pa6/stuff.es", "../pa6/stuff.en")

		After construction, access log-probability by 'myModel[native_word][foreign_word]'
		Just accessing 'myModel[native_word]' will return a Counter. Use .most_common(n)

		Similarly, a reverse dictionary will also be created which you can access by writing
			myModel.reverseMap[foreign_word][native_word]

		Caution: if the log-probability does not exist - it won't return float('-inf') so please
		check beforehand to see if something is in there: 
			myModel[existent_word].get(fakeword, float('-inf'))
		"""
		#create necessary maps here
		self.foreign_lines = []
		self.native_lines = []
		self.probabilityMap = collections.defaultdict(getDict)
		self.reverseMap = collections.defaultdict(getDict)
		if loadFile:
			self.loadFromFile(loadFile)
		elif foreign_file and native_file:
			self.readFile(foreign_file, native_file)
			self.train(iterations, Verbose)

	def loadFromFile(self, fileName):
		"""
		Loads a precomputed translation model from the disk.
		"""
		mapList = pickle.load( open( fileName, "rb"))
		self.probabilityMap = mapList[0]
		self.reverseMap = mapList[1]
		self.foreign_lines = mapList[2]
		self.native_lines = mapList[3]

	def saveToFile(self, fileName):
		"""
		Saves the data within this translation model to the disk.
		"""
		mapList = [self.probabilityMap, self.reverseMap, self.foreign_lines, self.native_lines]
		pickle.dump( mapList, open(fileName, "wb"), protocol=pickle.HIGHEST_PROTOCOL)

	def processSentence(self, line):
		"""
		Line should be a string.
		Removes numbers and punctuation.
		Returns a list of words
		"""
		#print line.lower()
		removeNumbers = r'(\d[\d\.\,\%]*[ .]\%? ?)|( \d[\d\.\,\%]*)'
		removePunctuation = r'(&.*?;)|( ?[\.\,\:\?])|¿\ | \-|\- '
		return re.sub(removeNumbers + '|' + removePunctuation, "", line.lower().strip()).split()


	def readFile(self, foreignName, nativeName):
		"""
		Loads in training data as list of lines - foreignName is the name of the file
		for the foreign text and nativeName is the name of the file for the native text
		"""
		with open(foreignName) as f:
			for line in f:
				words = self.processSentence(line)
				self.foreign_lines.append(words)
		with open(nativeName) as n:
			for line in n:
				words = ["<NULL>"]
				words += self.processSentence(line)
				self.native_lines.append(words)

	def train(self, iterations, Verbose=False):
		"""
		Trains the data and returns a map that can be indexed ["native word"]["foreign word"]
		and gets the log probablity of that word alignment
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
			for foreign_w, value in foreign_dict.iteritems():
				newVal = math.log(value)
				self.probabilityMap[native_w][foreign_w] = newVal
				self.reverseMap[foreign_w][native_w] = newVal

	def _normalize(self, initMap):
		"""
		Normalizes initMap so that the values of model["word"] sum to one
		"""
		for native_w, foreign_dict in initMap.iteritems():
			w_sum = sum(foreign_dict.values())
			for foreign_w in foreign_dict.keys():
				initMap[native_w][foreign_w] = initMap[native_w][foreign_w]/w_sum

	def __getitem__(self, index):
		return self.probabilityMap[index]

######FOR TESTING PURPOSES ONLY########
def main():
	spanish_file = "../pa6/es-en/train/europarl-v7.es-en.es"
	english_file = "../pa6/es-en/train/europarl-v7.es-en.en"

	# spanish_file = "../pa6/test.es"
	# english_file = "../pa6/test.en"

	model = ModelOne(spanish_file, english_file, Verbose=True)
	print "done"
	model.saveToFile("save.model")

	print model["house"]["casa"]
	# for span_line, eng_line in it.izip(model.foreign_lines, model.native_lines):
	# 	print "Spanish: ", span_line
	# 	print "English: ", eng_line

if __name__ == '__main__':
	main()
