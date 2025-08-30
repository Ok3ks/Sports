FROM python:3.12 AS base

# build and load all requirements
FROM base AS builder
WORKDIR /sports/app

# upgrade pip to the latest version
RUN apt-get update \
    && apt-get install -y build-essential libstdc++6 libgdal-dev gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL
ENV GDAL_CONFIG=/usr/bin/gdal-config

ARG DB_PORT
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_DATABASE
ARG DB_DRIVER_NAME
ARG DJANGO_SECRET_KEY
ARG REDISHOST
ARG REDISPORT

#setup environments
# COPY requirements.txt .
# RUN python3 -m venv /venv
# RUN pip install -r requirements.txt

# ENV PATH=/venv/bin:$PATH

# build a clean environment
FROM base

WORKDIR /sports
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONPATH=:$(pwd)

# virtual environment is copied
# COPY --from=builder /venv /venv

# bash is installed for more convenient debugging.
RUN apt-get update && apt-get -y install bash  && rm -rf /var/lib/apt/lists/*

# copy payload code only
WORKDIR /sports/LiveProject

COPY src/ ./src/ 
COPY LiveProject/ ./LiveProject/
COPY report_app ./report_app/
COPY container.sh . 

# COPY db.sqlite3 . 
# COPY .gitignore .
# ENV GOOGLE_ENTRYPOINT="/venv/bin/gunicorn --bind=8000 LiveProject.wsgi:application"

# RUN chmod +x /venv/bin/activate
RUN chmod +x ./container.sh

# RUN . /venv/bin/activate
RUN ./container.sh

EXPOSE 8000
ENTRYPOINT ["gunicorn", "--config=python:LiveProject.gunicorn"]
