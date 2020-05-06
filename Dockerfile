FROM apache/airflow:latest

MAINTAINER "Shivansh Saini" "shivansh.saini@headout.com"

ENV POETRY_VERSION 1.0.5
ENV PYTHONPATH ${AIRFLOW_HOME}

RUN pip install --user poetry==$POETRY_VERSION

# Poetry config: virtualenv not needed in docker, so turned off
RUN poetry config virtualenvs.create false

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ${AIRFLOW_HOME}/
# Project initialization
RUN poetry install --no-interaction --no-ansi

COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
COPY src/. ${AIRFLOW_HOME}/
COPY scripts/entrypoint.sh /entrypoint

EXPOSE 8080

USER airflow
WORKDIR ${AIRFLOW_HOME}

ENTRYPOINT [ "/usr/bin/dumb-init", "--", "/entrypoint" ]
CMD [ "webserver" ]
