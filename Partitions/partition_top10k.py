#!/bin/bash

infile=$1
outfile=$2
total=100
echo "SOURCES FOR TOP10K TWITTER ACCOUNTS SUMMARY" > $outfile
date >> $outfile
for src in social_baker MRW RDS social_baker_and_MRW social_baker_and_RDS MRW_and_RDS social_baker_and_MRW_and_RDS; do
  src_count=$(grep "'${src}'" $infile | wc -l)
  proportion=$(echo "scale=3; $src_count / $total" | bc)
  echo " " >> $outfile
  echo "Source: $src" >> $outfile
  echo "Accounts from source: $src_count" >> $outfile
  echo "Percentage of top10k from source: ${proportion}%" >> $outfile
done
date >> $outfile
