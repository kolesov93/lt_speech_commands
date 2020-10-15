#!/usr/bin/env python3
import sys
import shutil
import os
import random
import subprocess as sp

random.seed(1993)

try:
    shutil.rmtree('arena')
except Exception as ex:
    pass
os.mkdir('arena')

with open('words') as fin:
    words = [x.strip().replace(' ', '_') for x in fin.readlines()]

for word in words:
    os.mkdir('arena/' + word)
os.mkdir('arena/_background_noise_')

ncnt = 0
for full_fname in os.listdir('.'):
    if not full_fname.endswith('.wav'):
        continue

    fname, ext = full_fname.split('.')
    duration = float(sp.check_output(['soxi', '-D', full_fname]))
    with open(fname + '.txt') as fin:
        known_ids = set()
        lwords = []
        for line in fin:
            tokens = line.strip().split()
            assert len(tokens) == 3, line.strip()
            start, end, wid = float(tokens[0]), float(tokens[1]), int(tokens[2])
            assert wid not in known_ids, '{} {}'.format(wid, full_fname)
            known_ids.add(wid)
            assert wid == max(known_ids), '{} {}'.format(wid, full_fname)
            lwords.append((start, end, wid))

        for i, (start, end, wid) in enumerate(lwords):
            prevend = 0. if i == 0 else lwords[i - 1][1] + 0.1
            nextstart = duration if i + 1 == len(lwords) else lwords[i + 1][0] - 0.1
            if nextstart - prevend < 1.:
                print(full_fname, wid, 'too short pause', file=sys.stderr)
                continue
            if end - start > 1.:
                print(full_fname, wid, 'too long word', file=sys.stderr)
                continue

            realstart = start
            realend = end

            left = max(prevend, min(nextstart - 1., start - 0.1))
            right = start
            assert left <= right, '{} {} {} {}'.format(full_fname, wid, left, right)
            start = random.uniform(left, right)
            ofname = os.path.join('arena', words[wid - 1], '{}_nohash_{}.wav'.format(fname, 0))
            sp.check_call(['sox', full_fname, ofname, 'trim', '{:.04f}'.format(start), '1.0'])

            if realstart - prevend > 1.:
                ncnt += 1
                ofname = os.path.join('arena', '_background_noise_', '{}.wav'.format(ncnt))
                sp.check_call(['sox', full_fname, ofname, 'trim', '{:.04f}'.format(prevend), '{:.04f}'.format(realstart - prevend)])
            if i + 1 == len(lwords) and duration - realend > 1.:
                ncnt += 1
                ofname = os.path.join('arena', '_background_noise_', '{}.wav'.format(ncnt))
                sp.check_call(['sox', full_fname, ofname, 'trim', '{:.04f}'.format(realend), '{:.04f}'.format(duration - realend)])

