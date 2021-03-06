from datetime import timedelta

from airflow import DAG
from airflow.configuration import conf
from airflow.contrib.sensors.aws_sqs_sensor import SQSSensor
from airflow.utils import timezone
from airflow.utils.dates import days_ago

from ergo import SECTION_NAME
from ergo.operators.sqs.result_from_messages import JobResultFromMessagesOperator

TASK_ID_SQS_COLLECTOR = "collect_sqs_messages"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 10,
    'retry_delay': timedelta(minutes=2),
    'start_date': days_ago(1),
}

sqs_queue_url = conf.get(SECTION_NAME, "result_queue_url")

with DAG(
    'ergo_job_collector',
    default_args=default_args,
    is_paused_upon_creation=False,
    schedule_interval=timedelta(seconds=10),
    catchup=False,
    max_active_runs=1
) as dag:
    sqs_collector = SQSSensor(
        task_id=TASK_ID_SQS_COLLECTOR,
        sqs_queue=sqs_queue_url,
        max_messages=10,
        wait_time_seconds=10
    )

    result_transformer = JobResultFromMessagesOperator(
        task_id='process_job_result',
        sqs_sensor_task_id=TASK_ID_SQS_COLLECTOR
    )

sqs_collector >> result_transformer
