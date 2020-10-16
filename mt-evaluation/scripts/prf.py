import sys

def calc_precision(ref_sent, hyp_sent):
        """ Calculate precision given a reference and hypothesis sentence """
        
        ref_words = ref_sent.rstrip().split()
	hyp_words = hyp_sent.rstrip().split()
	precision = 0.0
	for hyp_word in hyp_words:
		if hyp_word in ref_words:
			precision += 1
	if len(hyp_words) < 1:
		return 0.0
	return precision / len(hyp_words)

def calc_recall(ref_sent, hyp_sent):
        """ Calculate recall given a reference and hypothesis sentence """
        
        ref_words = ref_sent.rstrip().split()
	hyp_words = hyp_sent.rstrip().split()
	recall = 0.0
	for ref_word in ref_words:
		if ref_word in hyp_words:
			recall += 1
	if len(ref_words) < 1:
		return 0.0
	return recall / len(ref_words)

def calc_fscore(ref_sent, hyp_sent, beta=1, precision=None, recall=None):
        """ Calculate F-score for a reference and hypothesis sentence using beta and input values (optional) for precision """
	
        if precision == None: precision = calc_precision(ref_sent, hyp_sent)
	if recall == None: 	  recall = calc_recall(ref_sent, hyp_sent)
	if precision == 0.0 and recall == 0.0:
		return 0.0
	f_score = (1 + beta*beta) * precision * recall / ( (precision*beta*beta) + recall)
	return f_score

def tp_fp_fn(ref_sent, hyp_sent):
	"""
	
	Input: 
	1. ref_sent (str): Reference sentence
	2. hyp_sent (str): Hypothesis sentence
	
	Description:
		-Calculates true positives, false positives and false negatives 
		checking only for membership in the original class,without taking 
		into account expected counts.

		-Example:
			Ref: the quick fox and the fast fox
			Hyp: the quick and the fast fox
		
	Output:
	1. tp_fp_fn (list): [true_positives, false_positives, false_negatives]
		
	"""
	ref_words = ref_sent.rstrip().split()
	hyp_words = hyp_sent.rstrip().split()
	tp = 0
	fp = 0
	fn = 0
	
	for hyp_word in hyp_words:
		if hyp_word in ref_words:
			tp += 1
			ref_idx = ref_words.index(hyp_word)
			del ref_words[ref_idx]
	fp = len(hyp_words)-tp
	
	ref_words = ref_sent.rstrip().split()
	hyp_words = hyp_sent.rstrip().split()

	for ref_word in ref_words:
		if ref_word not in hyp_words:
			fn += 1
	return [tp, fp, fn]

def main(ref, hyp):
	ref_file = open(ref,'r')
	hyp_file = open(hyp,'r')

	precision = 0.0
	recall = 0.0
	f1_score = 0.0

	true_positives = 0.0
	false_positives = 0.0
	false_negatives = 0.0

	ref_lines = ref_file.readlines()
	hyp_lines = hyp_file.readlines()
	N = len(ref_lines)
	print(N)
	i = 0

	for ref_sent, hyp_sent in zip(ref_lines, hyp_lines):

		tp, fp, fn = tp_fp_fn(ref_sent, hyp_sent)
		true_positives += tp
		false_positives += fp
		false_negatives += fn

	precision = true_positives / (true_positives + false_positives)
	recall = true_positives / (true_positives + false_negatives)
	f1_score = 2 * precision * recall / (precision + recall)
	
	print("Precision: ", precision)
	print("Recall   : ", recall)
	print("F-1 score: ", f1_score)

	ref_file.close()
	hyp_file.close()

if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2])
