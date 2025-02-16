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

ARG DB_PATH
ARG DJANGO_SECRET_KEY
ARG IS_SQLITE


#setup environments
COPY requirements.txt .
RUN python3 -m venv /venv
RUN /venv/bin/pip install -r requirements.txt

# build a clean environment
FROM base

WORKDIR /sports

# ENV PYTHONPATH="$PYTHONPATH:/Sports"

# virtual environment is copied
COPY --from=builder /venv /venv

# bash is installed for more convenient debugging.
# RUN apt-get update && apt-get -y install bash  && rm -rf /var/lib/apt/lists/*

# copy payload code only
WORKDIR /sports/LiveProject

COPY src/ ./src/ 
COPY LiveProject/ ./LiveProject/
COPY db.sqlite3 ./

COPY report_app ./report_app/


# ENV GOOGLE_ENTRYPOINT="/venv/bin/gunicorn --bind=8000 LiveProject.wsgi:application"

EXPOSE 8000
# ENTRYPOINT ["/venv/bin/gunicorn", "--config=python:LiveProject.gunicorn"]
