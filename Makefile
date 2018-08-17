#/usr/bin/sh
#
DATA_DIR :=samples/
OUTPUT :=tests/output
SCRIPT :=scripts
VERSION=0.4
DOC="."
DATA=data/quranic-corpus-morphology-0.4.txt
OUTDATA=output/quranic_corpus.csv
default: all
# Clean build files
corpus:
	# run stemmer
	python scripts/convert_quran_corpus_to_csv.py -f ${DATA} -o ${OUTDATA}

