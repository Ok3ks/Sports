FROM python:3.9-slim

WORKDIR /fast_api

COPY requirements.txt ./
COPY fpl ./
COPY api.py ./
COPY init_env.sh ./
COPY src ./src
COPY fpl ./


RUN pip install -r requirements.txt
RUN PYTHONPATH=${PYTHONPATH}:$(pwd)
#SHELL ["/bin/bash", "-c", "init_env.sh"]


#Add state of gameweek to DB instead 
#RUN ["python3", "update_gameweek_score.py" "-${gameweek}"] 
#if gameweek is ongoing, return response that gameweek is ongoing

EXPOSE  8080
#CMD python3 -m uvicorn api:app
CMD ["uvicorn", "api:app"]