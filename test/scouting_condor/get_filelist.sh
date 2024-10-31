#!/bin/bash

# Base directory
BASE="/store/data/Run2018A/ScoutingPFCommissioning/RAW/v1"
OUTPUT="PFComm_2018A.txt"

# Create a temporary directory for parallel processing
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Function to process a directory
process_dir() {
    local dir=$1
    local outfile=$2
    xrdfs root://xrootd.cmsaf.mit.edu/ ls -R $dir | grep "\.root$" >> "$outfile"
}
export -f process_dir

# Get list of all subdirectories
echo "Getting list of directories..."
xrdfs root://xrootd.cmsaf.mit.edu/ ls -R $BASE | grep "^/store" | grep "/000/" > $TMPDIR/dirs.txt

# Process directories in parallel
echo "Processing directories in parallel..."
cat $TMPDIR/dirs.txt | parallel -j 20 process_dir {} $TMPDIR/files_{#}.txt

# Combine all files and format output
echo "Combining results..."
cat $TMPDIR/files_*.txt | while read filepath; do
    echo "root://xrootd.cmsaf.mit.edu/${filepath}	${filepath##*/}"
done > $OUTPUT

# Count files
COUNT=$(wc -l < $OUTPUT)
echo "Found $COUNT files. Results written to $OUTPUT"