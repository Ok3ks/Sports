FROM python:3.9-slim

WORKDIR /fast_api

COPY ["src" "./"]
COPY ["requirements.txt", './']
COPY ["fpl", ""]

RUN pip install -r requirements.txt
RUN ["source", "init_env.sh"]

#ARG gameweek from check_gameweek
#Add state of gameweek to DB instead 
#RUN ["python3", "update_gameweek_score.py" "-${gameweek}"] 
#if gameweek is ongoing, return response that gameweek is ongoing


CMD ["uvicorn", "api:app"]