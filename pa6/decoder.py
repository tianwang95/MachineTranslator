#!/usr/bin/env python
#Implementation of IBM Model One Training

import itertools as it
import collections
import math
import codecs
import heapq
import nltk
import ModelOne
from itertools import izip
from LanguageModel import LanguageModel

MAX_STACK_LEN = 5

class Hypothesis:
	"""
	Represents a hypothesis with cost, words translated so far, and marks of which words
	have been covered.
	"""
	def __init__(self, chosen_word, covering, prev_hyp):
		self.chosen_word = chosen_word
		self.covering = covering
		self.cost = compute_cost()
		self.prev_hyp = prev_hyp
		self.total = prev_hyp.total + 1 if prev_hyp.total else 1

	def compute_cost(self):
		"""
		Current cost:
		The product of translation, distortion and language model probalities for each phrase.

		Future cost:
		Use Viterbi with language model translation
		"""
		#TRANSLATION COST: Get [foreign phrase][english phrase] from the dict
		#DISTORTION COST: That shit with phrase indices (Look up from slides)
		#LANGUAGE MODEL: Score the entire sentence using the lm


	def distortion_cost(self):
		

	def num_covered_foreign_words(self):
		return self.covering.count('1')

	def __cmp__(self, other):
		return cmp(self.cost, other.cost)

class Decoder:
	"""
	Implements a decoder for statistical MT.
	"""
	def __init__(self, phrase_table):
		self.phrase_table = phrase_table
		self.language_model = LanguageModel()

	def derive_new_hyps(self, src_sentence, hyp):
		"""
		returns all possible expansions of the given hypothesis.
		Loops through source sentence, starts expanding from each uncovered word.
		for all totally uncovered phrases that are in the dict,
			creates a new hypothesis with an updated covering and new phrase.
		returns the list of all the new hypotheses.
		"""
		new_hyps = []
		for i in xrange(src_sentence):
			if hyp.covering[i] == '1':
				continue
			cur_phrase = []
			j = 0
			while i+j < len(src_sentence):
				phrase.append(src_sentence[i + j])
				if phrase in self.phrase_table and hyp.covering[i + j] == '0':
					for eng_phrase, prob in self.phrase_table[phrase]:
						# create new hyp based on this phrase
						new_hyp = Hypothesis(eng_phrase, hyp.covering[:i] + '1' * (j + 1 - i) + covering[j+1:], hyp)
						new_hyps.append(new_hyp)
					j += 1
				else:
					break
		return new_hyps

	def beam_search_stack_decode(src_sentence):
		"""
		Assumes src_sentence is a list of tokens.
		"""
		hypStacks = [[] for i in len(src_sentence)]
		hypStacks[0].append(Hypothesis([], '0' * len(src_sentence),None))

		for hypStack in hypStacks:
			for hyp in hypStack:
				new_hyps = self.derive_new_hyps(hyp)
				for new_hyp in new_hyps:
					nf_new_hyp = new_hyp.covering.count('1')
					heapq.heappush(hypStacks[nf_new_hyp], new_hyp) #HEAP ORDER!
					if len(hypStacks[nf_new_hyp]) > MAX_STACK_LEN:
						#REMOVE LAST ELEMENT
						worst_hyp = heapq.nlargest(1)[0]
						idx = hypStacks[nf_new_hyp].find(worst_hyp)
						hypStacks[nf_new_hyp][idx] = hypStacks[nf_new_hyp][-1]
						hypStacks[nf_new_hyp].pop()
		#NEED TO RECOMBINE HYPOTHESES SOMEWHERE AROUND HERE

		return heapq.heappop(hypStacks[-1])








