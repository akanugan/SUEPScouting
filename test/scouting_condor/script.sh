#!/bin/bash
JOBNUM=$1
INPUT_FILE=$2
OUTPUT_FILE=$3
CMSSW_VERSION=$4

echo "Starting job ${JOBNUM} with input: ${INPUT_FILE}"
echo "Output will be: ${OUTPUT_FILE}"

# Setup environment
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc820
#source /cvmfs/cms.cern.ch/common/cmssw-el7 
#eval `/cvmfs/cms.cern.ch/common/cmssw-el7` 
#singularity exec --no-home -B /cvmfs,/afs,/eos,/srv /cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7 /bin/bash -c '
echo "Current OS version:"
cat /etc/os-release
echo "SINGULARITY_CONTAINER: $SINGULARITY_CONTAINER"

export HOME=.

# Setup CMSSW
echo "Setting up CMSSW..."
scramv1 project CMSSW ${CMSSW_VERSION}
cd ${CMSSW_VERSION}/src
eval `scramv1 runtime -sh`

mkdir -p ${CMSSW_BASE}/src/PhysicsTools
cd ${CMSSW_BASE}/src


echo "Copying CMSSW code..."
if [ -d "/srv/SUEPScouting" ]; then
    cp -rv /srv/SUEPScouting PhysicsTools/ || exit 1
elif [ -d "../../SUEPScouting" ]; then
    cp -rv ../../SUEPScouting PhysicsTools/ || exit 1
else
    echo "Error: Cannot find SUEPScouting directory"
    echo "Full directory structure:"
    find /srv -name "SUEPScouting" 2>/dev/null
    find $(dirname $(pwd))/.. -name "SUEPScouting" 2>/dev/null
    exit 1
fi


# Build
echo "Building CMSSW..."
scram b -j8

echo "Running cmsRun..."
cd PhysicsTools/SUEPScouting/test/
echo "Copying input file..."
xrdcp ${INPUT_FILE} ./input.root
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy input file"
    exit 1
fi
echo "Directory contents:"
ls -la 
cmsRun ScoutingNanoAOD_cfg.py inputFiles=file:./input.root outputFile=${OUTPUT_FILE} maxEvents=-1 isMC=false era=2018
if [ $? -ne 0 ]; then
    echo "Error: cmsRun failed"
    exit 1
fi

#check o/p
echo "ls after cmsRun:"
ls -la

echo "Copying output to MIT storage..."
xrdcp -v ${OUTPUT_FILE} root://submit50.mit.edu//data/user/a/akanugan/SUEP/PFComm_ntuples/${OUTPUT_FILE}
#xrdcp -v ${OUTPUT_FILE} root://submit50.mit.edu/akanugan/SUEP/${OUTPUT_FILE}
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy output file"
    exit 1
fi
ls -l ${OUTPUT_FILE}
voms-proxy-info


# Clean up
cd ../../../../
rm -rf ${CMSSW_VERSION}
rm input.root
rm ${OUTPUT_FILE}

echo "Job completed successfully"