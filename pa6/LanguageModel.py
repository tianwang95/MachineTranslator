#!/usr/bin/env python
#Implementation of an n-gram English Language Model
#Tian Wang, Bogac Kerem Goksel, Russell Kaplan, Duc Nguyen

from math import log
from collections import defaultdict

class LanguageModel:
	def __init__(self, unigram_file="../ngrams/1.txt", bigram_file="../ngrams/2.txt", trigram_file="../ngrams/3.txt"):
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
		self.unigramCounts = defaultdict(lambda: 1)
		self.bigramCounts = defaultdict(lambda: 0)
		self.trigramCounts = defaultdict(lambda: 0)
		self.totalUnigrams = 0
		self.train(unigram_file, bigram_file, trigram_file)

	def train(self, unigram_file, bigram_file, trigram_file):
		with open(unigram_file) as u:
			for line in u:
				token, count = line.split()
				self.unigramCounts[token] += count
				self.totalUnigrams += 1
		with open(bigram_file) as b:
			for line in b:
				count, token1, token2 = line.split()
				self.bigramCounts[token1 + " " + token2] = count
		with open(trigram_file) as t:
			for line in t:
				count, token1, token2, token3 = line.split()
				self.trigramCounts[token1 + " " + token2 + " " + token3] = count
		self.totalUnigrams += len(self.unigramCounts)
				


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
			bigram = sentence[0] + " " + sentence[1]
			count = self.bigramCounts[bigram]
			scoreModifier = 0.4
			if count:
				totalCount = self.unigramCounts[sentence[0]] - 1
			else:
				count = self.unigramCounts[sentence[1]]
				totalCount = self.totalUnigrams
				scoreModifier *= 0.4
			return log(count) - log(totalCount) + log(scoreModifier)
		else:
			for nextToken in sentence:
				if lastToken and secondToLastToken:
					trigram = secondToLastToken + " " + lastToken + " " + nextToken
					count = self.trigramCounts[trigram]
					scoreModifier = 1
					if count:
						totalCount = self.bigramCounts[secondToLastToken + " " + lastToken]
					else:
						bigram = lastToken + " " + nextToken
						count  = self.bigramCounts[bigram]
						scoreModifier *= 0.4
						if count:
							totalCount = self.unigramCounts[lastToken] - 1
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

