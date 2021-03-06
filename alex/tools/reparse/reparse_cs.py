#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
Reparse transcribed texts extracted from logs using Czech PTI handcrafted SLU.
In addition, abstract some values (stops, times).

Print abstracted and unabstracted utterances and DAs to standard output.

Usage:

    ./reparse_cs.py file.txt

The input file is assumed to be in the format provided by extract_texts.py.
"""

from alex.components.asr.utterance import Utterance
from alex.components.slu.base import CategoryLabelDatabase
from alex.applications.PublicTransportInfoCS.preprocessing import PTICSSLUPreprocessing
from alex.applications.PublicTransportInfoCS.hdc_slu import PTICSHDCSLU
from alex.utils.config import as_project_path

import argparse
import sys
import codecs
import re

def get_abutt_str(utt, abutt):
    """Abstract an utterance, return as string."""

    abutt_str = ''
    for i, tok in enumerate(abutt[0]):
        # check if the current position contains an abstracted slot
        m = re.match('^([A-Z_]+)=', tok)
        if m:
            slot = m.group(1)
            if slot == 'TASK':  # do not abstract TASK=..., use the original expression
                start = sum(abutt[2][0:i])
                length = abutt[2][i]
                abutt_str += ' '.join(utt[start:start+length])
            else:
                abutt_str += '*' + slot
        else:
            abutt_str += tok
        abutt_str += ' '
    return abutt_str.rstrip()


def abstract_da(best_da):
    """Abstract values in a DA (in-place)."""

    for dai in best_da:
        # abstract values of given slots
        if dai.name:
            if 'stop' in dai.name:
                dai.value = '*STOP'
            elif 'city' in dai.name:
                dai.value = '*CITY'
            elif 'date' in dai.name or 'time' in dai.name or 'ampm' in dai.name:
                dai.value = '*' + dai.name.upper()


def process_file(file_path):

    cldb = CategoryLabelDatabase(as_project_path('applications/PublicTransportInfoCS/data/database.py'))
    preprocessing = PTICSSLUPreprocessing(cldb)
    hdc_slu = PTICSHDCSLU(preprocessing, cfg = {'SLU': {PTICSHDCSLU: {'utt2da': as_project_path('applications/PublicTransportInfoCS/data/utt2da_dict.txt')}}})
    stdout = codecs.getwriter('UTF-8')(sys.stdout)

    with open(file_path, 'r') as fh:
        for line in codecs.getreader('UTF-8')(fh):
            line = line.strip("\r\n")

            # skip empty lines (dialogue boundaries)
            if not line:
                continue

            person, da, utt = line.split("\t")
            # skip system utterances, use just user utterances
            if 'SYSTEM' in person:
                continue

            # reparse utterance using transcription
            utt = re.sub(r',', r' ', utt)
            utt = Utterance(utt)
            sem = hdc_slu.parse({'utt': utt})

            # get abstracted utterance text
            abutt = hdc_slu.abstract_utterance(utt)
            abutt_str = get_abutt_str(utt, abutt)

            # get abstracted DA
            best_da = sem.get_best_da()
            best_da_str = unicode(best_da)
            abstract_da(best_da)

            print >> stdout, unicode(utt) + "\t" + abutt_str + "\t" + best_da_str + "\t" + unicode(best_da)


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('utt_file', help='file with utterances to reparse')

    args = ap.parse_args()
    process_file(args.utt_file)
