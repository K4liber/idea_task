#!/bin/bash
app="idea"
docker build -t ${app} .
docker stop ${app}
docker rm ${app}
docker run -d -p 8050:8050 \
  --name=${app} ${app}
