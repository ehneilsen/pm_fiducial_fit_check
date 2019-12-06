#!/bin/sh

DIRECTORY=/global/project/projectdirs/desi/users/skent/products
source ${DIRECTORY}/eups/bin/setups.sh
export EUPS_PATH=${DIRECTORY}
export EUPS_DIR=${DIRECTORY}/eups
export DATADIR=/project/projectdirs/desi/spectro/data
export PMDIR=/project/projectdirs/desi/engineering/platemaker/test
setup DB

touch data/everywhere_invenory.txt

MONTH=10
for DAY in $(seq -f "%02g" 10 31);  do
    NITE=2019${MONTH}${DAY}
    pgtcl -c "inv ${NITE} FVC" | grep "FVC everywhere script" | sed 's/^/'${NITE}\ '/g' >> data/everywhere_invenory.txt
done

MONTH=11
for DAY in $(seq -f "%02g" 1 18);  do
    NITE=2019${MONTH}${DAY}
    pgtcl -c "inv ${NITE} FVC" | grep "FVC everywhere script" | sed 's/^/'${NITE}\ '/g' >> data/everywhere_invenory.txt
done

