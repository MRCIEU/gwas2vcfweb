#!/usr/bin/env bash

# get data
curl -L http://csg.sph.umich.edu/abecasis/public/lipids2013/jointGwasMc_LDL.txt.gz | \
gzip -dc | \
cut -s -f2- | \
sed 's/^chr//g' | \
tr ':' '\t' | \
sed $'s/^SNP_hg19/chr\tpos/g' > example.txt