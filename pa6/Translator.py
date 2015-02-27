#!/usr/bin/env python
#Translation script for Machine Learning
#Tian Wang, Bogac Kerem Goksel, Russell Kaplan, Duc Nguyen
from os import system

from ModelOne import ModelOne, getDict
from LanguageModel import LanguageModel
import itertools as it
import collections
import math
import sys
import getopt

def translateSentences(sentences, model, langModel=None):
	outputSentences = []
	it = 0
	for foreign_s in sentences:
		if it%100==0:
			system("say " + str(it))
		currentSentence = ""
		for word in foreign_s:
			candidates = model.reverseMap[word].most_common(50)
			if candidates:
				bestWord = ""
				bestScore = float('-inf')
				for candidate_w in candidates:
					w_score = candidate_w[1] + langModel.score((currentSentence + candidate_w[0]).split())
					if w_score > bestScore:
						bestWord = candidate_w[0]
						bestScore = w_score
				currentSentence += (bestWord + " ")
			else: 
				currentSentence += (word + " ")
		print currentSentence
		it+=1

	return outputSentences


def main(argv):
	sentencesFile = "../pa6/es-en/dev/newstest2012.es"
	foreignFile = None
	nativeFile = None
	loadFile = "../pa6/save.model"
	ngramFile = None

	try:
		opts, args = getopt.getopt(argv, "is:f:n:l:g:")
	except getopt.GetoptError:
		print 'Wrong argument. Use -i for improved version'
		sys.exit(2)

	isImproved = False;

	for opt, value in opts:
		if opt == '-i':
			isImproved = True;
		elif opt == '-s':
			sentencesFile = value
		elif opt == '-f':
			foreignFile = value
		elif opt == '-n':
			nativeFile = value
		elif opt == '-l':
			loadFile = value
		elif opt == '-g':
			ngramFile = value

	# print "improved!" if isImproved else "Not improved!"
	# print sentencesFile
	# print foreignFile
	# print nativeFile
	# print loadFile

	if foreignFile and nativeFile:
		model = ModelOne(foreignFile, nativeFile)
	else:
		model = ModelOne(loadFile=loadFile)

	langModel = LanguageModel()

	if sentencesFile:
		sentences = []
		with open(sentencesFile) as f:
			for line in f:
				sentences.append(line.lower().strip().split())
		translated = translateSentences(sentences, model, langModel)
		# for sentence in translated:
		# 	print sentence


if __name__=='__main__':
	main(sys.argv[1:])