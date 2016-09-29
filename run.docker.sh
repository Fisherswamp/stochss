#!/bin/bash
docker rm stochsscontainer1_8_dev
if [[ $(uname -s) == 'Darwin' ]]
then
    PWD=$(pwd)
    docker run -it -p 8080:8080 -p 8000:8000 -p 9999:9999 --name=stochsscontainer1_8_dev --volume /Users:/Users briandrawert/stochss-launcher:1.8 sh -c "cd $PWD; ./run.ubuntu.sh --yy -a 0.0.0.0"
else
    docker run -it -p 8080:8080 -p 8000:8000 -p 9999:9999 --name=stochsscontainer1_8_dev --volume `pwd`:/stochss-master briandrawert/stochss-launcher:1.8 sh -c "cd /stochss-master; ./run.ubuntu.sh --yy -a 0.0.0.0"
fi


#sudo docker run -it --name=test_stochss --volume `pwd`:/stochss-master  stochss/stochss-launcher:1.7 /bin/bash
