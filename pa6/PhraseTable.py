#!/usr/bin/env python
#Implementation of IBM Model One Training

import itertools as it
import collections
import math
import codecs
import nltk
import ModelOne
from itertools import izip

class PhraseTable:
	"""
	Implements the six steps of building a phrase translation table.

	1. Gets a bitext from foreign_file and native_file.
	2. Parses and saves aligned sentences.
	"""
	def __init__(self, foreign_file, native_file, Verbose=False):
		self.foreign_sentences = []
		self.native_sentences = []
		with codecs.open(foreign_file, 'r', encoding='utf8') as f:
			self.foreign_sentences = f.readlines()
		with codecs.open(native_file, 'r', encoding='utf8') as f:
			self.native_sentences = f.readlines()
		self.fore_to_nat_model = ModelOne(foreign_file, native_file)
		self.nat_to_fore_model = ModelOne(native_file, foreign_file)

		for fsentence, nsentence in izip(self.foreign_sentences, self.native_sentences):
			fore_to_nat_alignments = build_alignments(self.fore_to_nat_model, fsentence, nsentence)
			nat_to_fore_alignments = build_alignments(self.nat_to_fore_model, nsentence, fsentence)

	def build_alignments(self, model, foreign_sentence, native_sentence):
		pass


######FOR TESTING PURPOSES ONLY########
def main():
	spanish_file = "../pa6/es-en/train/europarl-v7.es-en.es"
	english_file = "../pa6/es-en/train/europarl-v7.es-en.en"

	pt = PhraseTable(spanish_file, english_file, Verbose=True)


	

if __name__ == '__main__':
	main()
