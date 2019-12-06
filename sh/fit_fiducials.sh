#!/bin/sh
DIRECTORY=/global/project/projectdirs/desi/users/skent/products
source ${DIRECTORY}/eups/bin/setups.sh
export EUPS_PATH=${DIRECTORY}
export EUPS_DIR=${DIRECTORY}/eups
export DATADIR=/project/projectdirs/desi/spectro/data
export PMDIR=/project/projectdirs/desi/engineering/platemaker/test
setup desi
module swap PrgEnv-intel PrgEnv-gnu
export CC=$(which gcc)

Xvfb :6563 &
XVFBPID=$!
export DISPLAY=:6563

ORIG_DIR=${PWD}
while read LINE ; do
    EXPID=$(echo $LINE | cut -f2 -d' ')
    PADEXPID=$(printf "%08d" ${EXPID})
    NITE=$(echo $LINE | cut -f1 -d' ')
    mkdir data/${EXPID}
    cd data/${EXPID}
    ln -s /project/projectdirs/desi/users/skent/plate/desi/desitest/init.tcl .
    ln -s /project/projectdirs/desi/users/skent/plate/desi/etc/desi4/desi4.par .
    ln -s /project/projectdirs/desi/users/skent/plate/desi/etc/desi4/fiberpos-desi4.dat .
    ln -s /project/projectdirs/desi/spectro/data/${NITE}/${PADEXPID}/fvc-${PADEXPID}.fits.fz .
    imgMain -- <<EOF
    	    source init.tcl
	    desiParamRead desi4
            fvcParamRead desi4
            dmRead desi4
            fiducial2fif
            fiducialMerge ${EXPID}
            psolveSolve
            fiducialFit ${EXPID}
EOF
    cd $ORIG_DIR
done
kill ${XVFBPID}
