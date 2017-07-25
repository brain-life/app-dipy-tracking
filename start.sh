#!/bin/bash

#mainly to debug locally

if [ -z $SERVICE_DIR ]; then export SERVICE_DIR=`pwd`; fi
#ENV="IUHPC"

if [ $ENV == "SINGULARITY" ]; then
    
cat <<EOT > _run.sh
time singularity run /usr/local/images/brainlife_dipy-tracking.img
#check for output files
if [ -s track.tck ];
then
	echo 0 > finished
else
	echo "output_fe.mat missing"
	echo 1 > finished
	exit 1
fi
EOT

    chmod +x _run.sh
    nohup ./_run.sh > stdout.log 2> stderr.log & echo $! > pid
    exit
fi

#clean up previous job (just in case)
rm -f finished

if [ $ENV == "IUHPC" ]; then
	jobid=`qsub $SERVICE_DIR/submit.pbs`
	#jobid=`qsub -q preempt $SERVICE_DIR/submit.pbs`
	echo $jobid > jobid
fi

if [ $ENV == "VM" ]; then
	nohup time $SERVICE_DIR/submit.pbs > stdout.log 2> stderr.log &
	echo $! > pid
fi
