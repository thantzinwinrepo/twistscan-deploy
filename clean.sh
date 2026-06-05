#!/bin/bash
# clean.sh — wipe previous scan results before running a new domain
echo "Cleaning previous scan results..."
> ./output_urlscan.csv
> ./output_dnstwist.csv
rm -f ./screenshots/*.png
echo "Done. Ready for new scan."
