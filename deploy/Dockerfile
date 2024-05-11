FROM python:3.9-slim

WORKDIR /fast_api

COPY requirements.txt ./
COPY fpl ./
COPY api.py ./
COPY init_env.sh ./
COPY src ./src/
COPY fpl ./


RUN pip install -r requirements.txt
RUN PYTHONPATH=${PYTHONPATH}:$(pwd)
#SHELL ["/bin/bash", "-c", "init_env.sh"]


ENTRYPOINT [  ]