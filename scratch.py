#!/usr/bin/env python

from octavo.recommend.similarity import *

aid = 8398291
bid = 4642710
sim = ReviewerSimilarity()

print "Euclidean Ranks: "
for item in sim.euclidean_rank(aid):
    print "%s: %0.4f" % item
print
print "Pearson Ranks: "
for item in sim.pearson_rank(aid):
    print "%s: %0.4f" % item
