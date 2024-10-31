#!/bin/bash

# Setup environment
source /cvmfs/cms.cern.ch/cmsset_default.sh
#source /cvmfs/oasis.opensciencegrid.org/mis/osg-wn-client/current/el7-x86_64/setup.sh
export SCRAM_ARCH=slc7_amd64_gcc820


mkdir -p log
#voms-proxy-init -voms cms -valid 192:00
cp /tmp/x509up_u$(id -u) x509up
chmod +x script.sh

echo "Submitting condor jobs..."
condor_submit submit_scouting.sub
