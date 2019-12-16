#!/bin/sh

set -x

DIRECTORY=/global/project/projectdirs/desi/users/skent/products
source ${DIRECTORY}/eups/bin/setups.sh
export EUPS_PATH=${DIRECTORY}
export EUPS_DIR=${DIRECTORY}/eups
export DATADIR=/project/projectdirs/desi/spectro/data
export PMDIR=/project/projectdirs/desi/engineering/platemaker/test
setup DB

touch data/everywhere_inventory.txt

MONTH=10
for DAY in $(seq -f "%02g" 10 31);  do
    NITE=2019${MONTH}${DAY}
    pgtcl -c "inv ${NITE} FVC" | grep "FVC everywhere script" | sed 's/^/'${NITE}\ '/g' >> data/everywhere_inventory.txt
done

MONTH=11
for DAY in $(seq -f "%02g" 1 30);  do
    NITE=2019${MONTH}${DAY}
    pgtcl -c "inv ${NITE} FVC" | grep "FVC everywhere script" | sed 's/^/'${NITE}\ '/g' >> data/everywhere_inventory.txt
done

MONTH=12
for DAY in $(seq -f "%02g" 1 32);  do
    NITE=2019${MONTH}${DAY}
    pgtcl -c "inv ${NITE} FVC" | grep "FVC everywhere script" | sed 's/^/'${NITE}\ '/g' >> data/everywhere_inventory.txt
done

