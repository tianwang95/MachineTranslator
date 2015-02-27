#!/usr/bin/env python
#Implementation of an n-gram English Language Model
#Tian Wang, Bogac Kerem Goksel, Russell Kaplan, Duc Nguyen

from math import log
import collections

class LanguageModel:
	def __init__(self, unigram_file="../pa6/ngrams/1.txt", bigram_file="../pa6/ngrams/2.txt", trigram_file="../pa6/ngrams/3.txt"):
		'''
			unigram_file: the path to the text file that contains the unigram unigramCounts
							its expected format is: 
							token count
			bigram_file: the path to the text file that contains the unigram bigramCounts 
							its expected format is:
							count token1 token2
			trigram_file:  the path to the text file that contains the unigram trigramCounts
							its expected format is:
							count token1 token2 token3

			The language trains itself upon initialization and can score any sentence afterwards.
			It uses a stupid backoff with Laplace-smoothed unigrams.
		'''
		self.unigramCounts = collections.defaultdict(lambda: 1)
		self.bigramCounts = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
		self.bigramsWithStartingUnigram = collections.defaultdict(lambda: 1)
		self.trigramCounts = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
		self.trigramsWithStartingBigram = collections.defaultdict(lambda: 1)
		self.totalUnigrams = 0
		self.train(unigram_file, bigram_file, trigram_file)

	def unigramScore(self, word):
		return log(self.unigramCounts[word]) - log(self.totalUnigrams) - log(0.16)

	def train(self, unigram_file, bigram_file, trigram_file):
		with open(unigram_file) as u:
			for line in u:
				token, count = line.split()
				self.unigramCounts[token] += int(count)
				self.totalUnigrams += int(count)
		with open(bigram_file) as b:
			for line in b:
				count, token1, token2 = line.split()
				self.bigramCounts[token1][token2] += int(count)
		with open(trigram_file) as t:
			for line in t:
				count, token1, token2, token3 = line.split()
				self.trigramCounts[token1 + " " + token2][token3] += int(count)
		self.totalUnigrams += len(self.unigramCounts)
		for startWord, bigrams in self.bigramCounts.iteritems():
			self.bigramsWithStartingUnigram[startWord] = sum([val for key, val in bigrams.iteritems()])
			print "updated, ", self.bigramsWithStartingUnigram[startWord]
		for beginning, trigrams in self.trigramCounts.iteritems():
			self.trigramsWithStartingBigram[beginning] = sum([val for key, val in trigrams.iteritems()])
			print "updated, ", self.trigramsWithStartingBigram[beginning]				

				


	def score(self, sentence):
		'''
			score takes a sentence(a list of words), and scores it using the language model.
		'''
		score = 0.0
		lastToken = ""
		secondToLastToken = ""
		if len(sentence) == 1:
			return log(self.unigramCounts[sentence[0]]) - log(self.totalUnigrams) + log(0.4*0.4)
		elif len(sentence) == 2:
			count = self.bigramCounts[sentence[0]][sentence[1]]
			scoreModifier = 0.4
			if count:
				totalCount = self.bigramsWithStartingUnigram[sentence[0]]
			else:
				count = self.unigramCounts[sentence[1]]
				totalCount = self.totalUnigrams
				scoreModifier *= 0.4
			return log(count) - log(totalCount) + log(scoreModifier)
		else:
			for nextToken in sentence:
				if lastToken and secondToLastToken:
					bigram = secondToLastToken + " " + lastToken
					count = self.trigramCounts[bigram][nextToken]
					scoreModifier = 1
					if count:
						totalCount = self.trigramsWithStartingBigram[bigram]
					else:
						count  = self.bigramCounts[lastToken][nextToken]
						scoreModifier *= 0.4
						if count:
							totalCount = self.bigramsWithStartingUnigram[lastToken]
						else:
							count = self.unigramCounts[nextToken]
							totalCount = self.totalUnigrams
							scoreModifier *= 0.4
					score += log(count)
					score -= log(totalCount)
					score += log(scoreModifier)
				secondToLastToken = lastToken
				lastToken = nextToken
		return score
