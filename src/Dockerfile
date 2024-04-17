FROM python:3.9-slim as base
FROM base as builder

WORKDIR /db

RUN apt-get update \
    && apt-get -y upgrade \
    && pip install --upgrade pip 


COPY setup.py ./
RUN pip install --prefix=/install .

FROM base
WORKDIR /db

COPY --from=builder /install /usr/local

COPY /db .

#SHELL ["/bin/bash", "-c", "init_env.sh"]
RUN PYTHONPATH=${PYTHONPATH}:$(pwd)
ENTRYPOINT ["python", "/db/entry_point.py"]