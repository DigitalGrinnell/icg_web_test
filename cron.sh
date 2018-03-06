#!/bin/bash
echo 'This is cron.sh for icg_web_test on DGDockerX'
cd /home/mcfatem/Projects/Docker/icg_web_test
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
/usr/bin/docker build -t icg_web_test .
/usr/bin/docker-compose -f docker-compose.yml run icg_web_test
