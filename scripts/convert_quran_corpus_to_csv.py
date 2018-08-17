#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  convert_quran_corpus_to_csv.py
#  
#  Copyright 2018 zerrouki <zerrouki@majd4>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
# convert Quran corpus to csv format
import argparse
#~ filename ="../data/quranic-corpus-morphology-0.4.txt"
try:
    import pyarabic.trans
except:
    import sys
    print("You need to install pyarabic >= 0.6.5")
    sys.exit()
import pyarabic.araby as araby
import pandas as pd
from  pyarabic.arabrepr import arepr

def ajust(word):
    """ ajust some specific notation in words """
    
    # ajust small alef
    word = word.replace(araby.ALEF+araby.MINI_ALEF, araby.ALEF)
    word = word.replace(araby.ALEF_MAKSURA+araby.MINI_ALEF, araby.ALEF_MAKSURA)
    word = word.replace(araby.MINI_ALEF, araby.ALEF)

    word = word.replace("^", "")
    word = word.replace("@", "")
    word = word.replace("#", "")
    word = word.replace(".", "")
    word = word.replace("]", "")
    return word
    
def extract_features(features):
    """ extract features from code string"""
    fields = {"root":"",
    "lem":"",
    "pos":"",
    "type":"",
    "ext":[],
    }
    chunks = features.split('|')
    # first field is the word type
    fields['type'] = chunks[0]
    for chunk in chunks[1:]:
        parts = chunk.split(':')
        if len(parts) ==2:
            key, value = parts
            key = key.lower()
            if key in fields:
                fields[key]= value
        else:
            fields["ext"].append(chunk)
    if "root" in fields:
        fields["root"] = pyarabic.trans.convert(fields["root"], 'tim','arabic')
        fields["root"] = pyarabic.araby.normalize_hamza(fields["root"])
        fields["root"] = fields["root"].replace(araby.ALEF, araby.HAMZA)
        
    if "lem" in fields:
        fields["lem_voc"] = ajust(pyarabic.trans.convert(fields["lem"], 'tim','arabic'))
        fields["lem"] = pyarabic.araby.strip_tashkeel(fields["lem_voc"])
    fields["ext"] = ";".join(fields["ext"])
    return fields

def treat_line(line, previous={}):
    """
    Treat and extract fields from line
    LOCATION    FORM    TAG FEATURES
    """
    chunks = line.strip().split('\t')
    fields = {}
    if len(chunks) == 4:
        location, form, tag, features = chunks
        form = ajust(form)
        features  = extract_features(features)
        type_current = features.get('type','')
        type_previous = previous.get('type','')
        # if the previous is a prefix add it to current line
        if type_previous == "PREFIX" or type_current == "SUFFIX":
            form = previous['tim'] + form
        voc = pyarabic.trans.convert(form, 'tim','arabic')
        voc = ajust(voc)
        word = pyarabic.araby.strip_tashkeel(voc)
        #in case of suffix, it will take revious features
        fields = {"loc":location,
        "word":word,
        "tim":form,
        "voc":voc,
        "tag":tag,
        }
        # separate features
        fields.update(features)
        if type_current == "SUFFIX":
            # take some previous features 
            fields["loc"] = previous.get('loc','')
            fields["tag"] = previous.get('tag','')
            fields["root"] = previous.get('root','')
            fields["lem"] = previous.get('lem','')
            fields["lem_voc"] = previous.get('lem_voc','')
            fields["pos"] = previous.get('pos','')
            fields["type"] = previous.get('type','')
            fields["ext"] = previous.get('ext','')+":"+ features["ext"]            
            
    return fields

def get_line_type(line):
    """
    Treat and extract the type value only from line
    LOCATION    FORM    TAG FEATURES
    """
    chunks = line.strip().split('\t')
    if len(chunks) == 4:
        location, form, tag, features = chunks
        return features.split('|')[0]
    return ''
def grabargs():
    parser = argparse.ArgumentParser(description='Convert Quran Corpus into CSV format.')
    # add file name to import and filename to export
    parser.add_argument("-f", dest="filename", required=True,
    help="input file to convert", metavar="FILE")
    parser.add_argument("-o", dest="outfile", required=True,
    help="input file to convert", metavar="OUT_FILE")
    args = parser.parse_args()
    return args


def main(args):
    args = grabargs()
    filename = args.filename
    outfile  = args.outfile
    # read file
    data_list = []
    previous = {}
    cpt = 0
    limit = 1000000
    with open(filename, 'r') as infile:
        for line in infile:
            cpt += 1
            if cpt >= limit:
                break
            if not line.startswith("#"):

                type_current  = get_line_type(line)
                type_previous = previous.get('type','')
                #~ print type_current,"*", type_previous

                if not (type_previous == "PREFIX" or type_current == "SUFFIX"):
                        # flush previous 
                        data_list.append(previous)
                # treat new
                data_line = treat_line(line, previous)                        
                #~ previous = {}
                previous = data_line
    if previous:
        data_list.append(previous)
                
                
    df = pd.DataFrame(data_list)
    print(df.head(20))
    df.to_csv(outfile, sep='\t', encoding='utf-8', index = False)
    ## avoid empty fields
    df2 = df[['word', 'root', 'lem','tag']]
    import numpy as np
    #~ df2 = df2.replace(np.nan, 'word', regex=True)
    df2 = df2.dropna()
    #~ df2= 
    df2.to_csv(outfile+".dataset", sep='\t', encoding='utf-8', index = False)

            
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
