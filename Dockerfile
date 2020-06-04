FROM apache/airflow:latest

MAINTAINER "Shivansh Saini" "shivansh.saini@headout.com"

# Needed to not install system-globally
ENV PIP_USER 'yes'
ENV POETRY_VERSION 1.0.5
ENV PYTHONPATH ${AIRFLOW_HOME}

RUN pip install --user poetry==$POETRY_VERSION

# Poetry config: virtualenv not needed in docker, so turned off
RUN poetry config virtualenvs.create false

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ${AIRFLOW_HOME}/
# Project initialization
RUN poetry install --no-interaction --no-ansi

EXPOSE 8080

USER airflow
WORKDIR ${AIRFLOW_HOME}

COPY config/airflow.cfg ./airflow.cfg
COPY src/. ./
COPY build/. ./
COPY scripts/entrypoint.sh /entrypoint

ENTRYPOINT [ "/usr/bin/dumb-init", "--", "/entrypoint" ]
CMD [ "webserver" ]
