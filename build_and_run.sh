#!/bin/bash
app="idea"
docker_file="DockerfileUbuntu"
if [ "${1}" != "" ] ; then
  echo 'yolo'
  docker_file=$1
fi
echo 'Building with docker_file =' "${docker_file}"
docker build -t ${app} . -f "${docker_file}"
docker stop ${app}
docker rm ${app}
docker run -d -p 8050:8050 \
  --name=${app} ${app}
