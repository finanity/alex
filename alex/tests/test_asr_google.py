#!/usr/bin/env python
# -*- coding: utf-8 -*-

import __init__

import alex.utils.audio as audio

from alex.components.asr.google import GoogleASR
from alex.utils.mproc import SystemLogger

if __name__ == '__main__':
    print "Testing Google ASR service"
    print "=" * 120
    print
    language = 'en'
    sample_rate = 16000

    print "Language:       ", language
    print "Sample rate:    ", sample_rate
    print

    cfg = {
        'Audio': {
        'sample_rate': sample_rate
        },
        'ASR': {
            'Google': {
                'debug': False,
                'language': language,
                'maxresults': 5,
                'key': 'PRIVATE KEY'
            }
        },
        'Logging': {
            'system_logger': SystemLogger(stdout=True, output_dir='./call_logs'),
        },
    }

    asr = GoogleASR(cfg)

    # testing audio
    wav = audio.load_wav(cfg, './resources/test16k-mono.wav')

    print 'calling ASR'
    hyp = asr.recognize(wav)

    print 'expected hypothesis'
    print "I'm looking for a bar"

    print 'hypotheses'
    print hyp
