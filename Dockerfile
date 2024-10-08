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
ARG REDIS_HOST
ARG REDIS_PORT
ARG DJANGO_SECRET_KEY
#setup environments
COPY requirements.txt .
RUN python3 -m venv /venv
RUN /venv/bin/pip install -r requirements.txt

# build a clean environment
FROM base

WORKDIR /sports
COPY src/ ./src/ 

# ENV DJANGO_SECRET_KEY="django-insecure-f&xs472(b!o6_b$5l*--ea1*m^*_=y))edubhvkol3t4%2*#a_"
ENV PYTHONPATH="$PYTHONPATH:/sports"

# virtual environment is copied
COPY --from=builder /venv /venv

# bash is installed for more convenient debugging.
# RUN apt-get update && apt-get -y install bash  && rm -rf /var/lib/apt/lists/*

# copy payload code only
WORKDIR /sports/app
COPY app/ ./

# RUN ["/bin/bash", "init_env.sh"]
# RUN ["/bin/bash", "auth.sh"]
WORKDIR /sports/app/LiveProject

EXPOSE 8000
ENTRYPOINT ["/venv/bin/gunicorn", "--config=python:LiveProject.gunicorn"]
