from datetime import datetime, timedelta

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.contrib.sensors.aws_sqs_sensor import SQSSensor
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
    'schedule_interval': '@hourly',
}

queue_url = "http://sqs:9324/queue/{{ params.queue }}"

with DAG('example_sqs', default_args=default_args, params={
    'queue': 'default'
}) as dag:
    start_task  = DummyOperator(task_id= "start")
    stop_task   = DummyOperator(task_id= "stop")
    date_cmd_task = BashOperator(
        task_id="date",
        bash_command="date",
        xcom_push=True
    )

    sqs_task = SQSSensor(
        task_id='sqs',
        sqs_queue=queue_url,
        mode='reschedule'
    )

start_task >> date_cmd_task >> sqs_task >> stop_task
