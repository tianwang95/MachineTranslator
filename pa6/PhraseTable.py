#!/usr/bin/env python
#Implementation of IBM Model One Training

import itertools as it
import collections
import math
import codecs
from ModelOne import ModelOne,getDict
from itertools import izip

def getCounter():
	return collections.Counter()

class PhraseTable:
	"""
	Implements the six steps of building a phrase translation table.

	1. Gets a bitext from foreign_file and native_file.
	2. Parses and saves aligned sentences.
	"""
	def __init__(self, foreign_file, native_file, Verbose=False):
		self.foreign_sentences = []
		self.native_sentences = []
		self.phrase_dict = collections.defaultdict(getCounter)
		self.reverse_phrase_dict = collection.defaultdict(getCounter)

		self.phrase_counts = collections.defaultdict(lambda: collections.defaultdict(lambda: 0.0))

		self.fore_to_nat_model = ModelOne(loadFile="english-spanish.model")#rows are span
		self.nat_to_fore_model = ModelOne(loadFile="spanish-english.model")#rows are engl
		
		with open(foreign_file) as f:
			for line in f:
				line_tokenized = self.fore_to_nat_model.processSentence(line)
				self.foreign_sentences.append(line_tokenized)
		with open(native_file) as f:
			for line in f:
				line_tokenized = self.nat_to_fore_model.processSentence(line)
				self.native_sentences.append(line_tokenized)
		
		for fsentence, nsentence in izip(self.foreign_sentences, self.native_sentences):
			if len(fsentence) != 0 and len(nsentence) != 0:
				fore_to_nat_alignments = self.build_alignments(self.fore_to_nat_model, fsentence, nsentence)
				nat_to_fore_alignments = self.build_alignments(self.nat_to_fore_model, nsentence, fsentence)
				phrase_align_table = self.build_phrase_align_table(fore_to_nat_alignments, nat_to_fore_alignments)
				self.extract_phrases(phrase_align_table, fsentence, nsentence)

		self.normalize_table()
		print self.phrase_dict
		"""
		fsentence = ["maria", "no", "dio", "una", "bofetada", "a", "la", "bruja", "verde"]
		nsentence = ["mary", "did", "not", "slap", "the", "green", "witch"]
		"""
		"""
		fsentence = ['lamentablemente', 'queda', 'mucho', 'camino', 'por', 'recorrer']
		nsentence = ['unfortunately', 'there', 'is', 'a', 'long', 'way', 'to', 'go']
		"""
		"""
		f_aligns = [0, 2, 3, 3, 3, 1, 4, 6, 5]
		n_aligns = [0, 1, 1, 4, 6, 8, 7]
		phrase_align_table = self.build_phrase_align_table(f_aligns,n_aligns)
		print phrase_align_table
		self.extract_phrases(phrase_align_table, fsentence, nsentence)
		print self.phrase_counts
		"""
	def __getitem__(self, index):
		return self.phrase_dict[index]

	def reverse_phrase_align_table(self,phrase_align_table):
		reverse_table = collections.defaultdict(lambda:set([]))
		for native_index,alignments in phrase_align_table.iteritems():
			for alignment in alignments:
				reverse_table[alignment].add(native_index)
		return reverse_table

	def extract_phrases(self, phrase_align_table, fsentence, nsentence):
		rev_phrase_align_table = self.reverse_phrase_align_table(phrase_align_table)
		horizontal_phrases = self.get_contained_phrases(phrase_align_table, False)
		vertical_phrases = self.get_contained_phrases(rev_phrase_align_table, True)
		chunk_dict = self.get_extracted_chunks(phrase_align_table, horizontal_phrases, vertical_phrases)
		all_phrases_set = collections.OrderedDict()

		### getting phrase combos ###
		chunk_dict_list = chunk_dict.items()
		prev_phrase_tail = chunk_dict_list[0][0][len(chunk_dict_list[0][0])-1]
		prev_phrase = chunk_dict_list[0][0]
		prev_phrase_isHorizontal = chunk_dict_list[0][1]
		for phrase, isHorizontal in chunk_dict_list[1:]:
			curr_phrase_head = phrase[0]
			if curr_phrase_head[0] - 1 == prev_phrase_tail[0] and curr_phrase_head[1] - 1 == prev_phrase_tail[1]:
				pair_one = self.phrase_to_word(prev_phrase, fsentence, nsentence, prev_phrase_isHorizontal)
				pair_two = self.phrase_to_word(phrase, fsentence, nsentence, isHorizontal)
				native_string = pair_one[0] + " " + pair_two[0]
				fore_string = pair_one[1] + " " + pair_two[1]
				#update map
				self.phrase_counts[native_string][fore_string] += 1.0
			elif curr_phrase_head[0] - 1 == prev_phrase_tail[0] and curr_phrase_head[1] + 1 == prev_phrase_tail[1]:
				pair_one = self.phrase_to_word(phrase, fsentence, nsentence, isHorizontal)
				pair_two = self.phrase_to_word(prev_phrase, fsentence, nsentence, isHorizontal)
				native_string = pair_two[0] + " " + pair_one[0]
				fore_string = pair_one[1] + " " + pair_two[1]
				#update map
				self.phrase_counts[native_string][fore_string] += 1.0
			#updates
			prev_phrase_tail = phrase[len(phrase)-1]
			prev_phrase = phrase
			prev_phrase_isHorizontal = isHorizontal


				
		### getting sub phrases
		for phrase, isHorizontal in chunk_dict.iteritems():
			sub_phrases_list = sub_phrases(phrase)
			for sub_phrase in sub_phrases_list:
				all_phrases_set[sub_phrase] = isHorizontal

		for phrase, isHorizontal in all_phrases_set.iteritems():
			pair = self.phrase_to_word(phrase, fsentence, nsentence, isHorizontal)
			self.phrase_counts[pair[0]][pair[1]] += 1.0
	
	def get_extracted_chunks(self, phrase_align_table, horizontal_phrases, vertical_phrases):
		chunkSet = collections.OrderedDict() # key: phrase , value: isHorizontal
		for native_index, alignment_set in phrase_align_table.iteritems():
			for fore_index in alignment_set:
				curr_alignment = (native_index, fore_index)
				horizontal_index = self.get_alignment_in_phrase_list(curr_alignment, horizontal_phrases)
				vertical_index = self.get_alignment_in_phrase_list(curr_alignment, vertical_phrases)
				if (len(horizontal_phrases[horizontal_index]) >= len(vertical_phrases[vertical_index])):
					chunkSet[horizontal_phrases[horizontal_index]] = True
				else:
					chunkSet[vertical_phrases[vertical_index]] = False
		return chunkSet

	def get_alignment_in_phrase_list(self, alignment, phrase_list): #alignment is (native, fore) tuple
		for i, phrase in enumerate(phrase_list):
			if alignment in phrase:
				return i
		return -1

	def phrase_to_word(self, phrase, fsentence, nsentence, isHorizontal):
		if isHorizontal:
			native_phrase = nsentence[phrase[0][0]]
			fore_phrase = ""
			for alignment in phrase:
				fore_phrase += (fsentence[alignment[1]] + " ")
		else:
			fore_phrase = fsentence[phrase[0][1]]
			native_phrase = ""
			for alignment in phrase:
				native_phrase += (nsentence[alignment[0]] + " ")
		return (native_phrase.strip(), fore_phrase.strip())
	
	def get_contained_phrases(self, phrase_align_table, isFlipped):
		phrase_list = []
		for index, alignments in phrase_align_table.iteritems():
			sorted_alignments = sorted(alignments)
			prev = sorted_alignments[0]
			contig_alignments = [((index, prev) if not isFlipped else (prev, index))]
			for alignment in sorted_alignments[1:]:
				if alignment == prev + 1 or prev == -1:
					contig_alignments.append((index, alignment) if not isFlipped else (alignment, index))
					prev = alignment
				else:
					phrase_list.append(tuple(contig_alignments))
					contig_alignments = [((index, alignment) if not isFlipped else (alignment, index))]
					prev = alignment
			phrase_list.append(tuple(contig_alignments))
		return phrase_list 
					

		
	
	def build_alignments(self, model, foreign_sentence, native_sentence):
		"""
		returns list which contains index in native sentence of best translation
		of each word in foreign sentence
		"""
		alignment_list = [] #alignment list to return
		for i,fword in enumerate(foreign_sentence):
			max_score = float('-inf')
			best_trans= "" #best nword for current fword
			for j,nword in enumerate(native_sentence):
				curr_score = model[fword][nword]
				if curr_score>max_score:
					max_score = curr_score
					best_trans = nword
					best_trans_ind = j
			alignment_list.append(best_trans_ind)
		return alignment_list
	
	def build_phrase_align_table(self, fore_to_nat_table, nat_to_fore_table):
		phrase_align_table = collections.defaultdict(lambda: set()) #{nativeIndex : set([foreignIndices])}
		fore_to_nat_align_not_in_table = []
		nat_to_fore_align_not_in_table = nat_to_fore_table

		"""
		-The following loop creates the intersection of the two word-alignment tables.
		-foreignIndex is index for for->nat, alignment is corr index in nat->for
		"""
		for foreignIndex,alignment in enumerate(fore_to_nat_table):
			if nat_to_fore_table[alignment] == foreignIndex:        					
				fore_to_nat_align_not_in_table.append(-1)#remove alignment from "not-in" tables
				nat_to_fore_align_not_in_table[alignment] = -1
				phrase_align_table[alignment].add(foreignIndex)
			else:
				fore_to_nat_align_not_in_table.append(alignment)


		table_has_changed = True
		while table_has_changed:
			table_has_changed = False
			for i,alignment in enumerate(fore_to_nat_align_not_in_table):
				if alignment != -1 and self.should_add_to_table(alignment,i,phrase_align_table):
					phrase_align_table[alignment].add(i)	
					fore_to_nat_align_not_in_table[i] = -1
					table_has_changed = True
			for j,alignment in enumerate(nat_to_fore_align_not_in_table):
				if alignment != -1 and self.should_add_to_table(j,alignment,phrase_align_table):
					phrase_align_table[j].add(alignment)
					nat_to_fore_align_not_in_table[j] = -1
					table_has_changed = True

		return phrase_align_table
						
	def should_add_to_table(self,native_index,foreign_index,phrase_align_table):
		has_vertical_neighbors = False
		for diff in [-1,1]:#check if current alignment has vert neighbors
			if (native_index+diff in phrase_align_table) and (foreign_index in phrase_align_table[native_index+diff]):
				has_vertical_neighbors = True
		has_horizontal_neighbors = False
		for diff in [-1,1]:#check if current alignment has horiz
			if (native_index in phrase_align_table) and (foreign_index+diff in phrase_align_table[native_index]):
				has_horizontal_neighbors = True
		return has_vertical_neighbors + has_horizontal_neighbors == 1


	def normalize_table(self):
		for native_phrase, fore_dict in self.phrase_counts.iteritems():
			total = math.log(sum(fore_dict.values()))
			for fore_phrase, count in fore_dict.iteritems():
				self.phrase_dict[native_phrase][fore_phrase] = math.log(count) - total
				self.reverse_phrase_dict[fore_phrase][native_phrase] = math.log(count) - total

def sub_phrases(phrase):#phrase is a tuple of tuples, each tuple is coordinate in phrase_align_table
	sub_phrases = []
	for i in xrange(len(phrase)):
		for j in xrange(i+1,len(phrase)+1):
			cur_sub_phrase = phrase[i:j]
			sub_phrases.append(cur_sub_phrase)
	return tuple(sub_phrases)

######FOR TESTING PURPOSES ONLY########
def main():
	spanish_file = "../pa6/es-en/train/europarl-v7.es-en.es"
	english_file = "../pa6/es-en/train/europarl-v7.es-en.en"

	pt = PhraseTable(spanish_file, english_file, Verbose=True)


	

if __name__ == '__main__':
	main()
