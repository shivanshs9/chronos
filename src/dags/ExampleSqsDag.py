from datetime import datetime, timedelta

from airflow import DAG
from airflow.contrib.sensors.aws_sqs_sensor import SQSSensor
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.ergo import ErgoTaskProducerOperator
from airflow.sensors.ergo import ErgoJobResultSensor
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=30),
    'start_date': days_ago(1),
}

with DAG(
    'example_sqs',
    default_args=default_args,
    schedule_interval='@hourly'
) as dag:
    start_task  = DummyOperator(task_id= "start")
    stop_task   = DummyOperator(task_id= "stop")

    push_task_to_sqs = ErgoTaskProducerOperator(
        task_id='example_task_pusher',
        ergo_task_id='noArg'
    )

    wait_job_result = ErgoJobResultSensor(
        task_id='example_job_sensor',
        ergo_task_id='noArg'
    )


start_task >> push_task_to_sqs >> wait_job_result >> stop_task
