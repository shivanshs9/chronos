from datetime import timedelta

from airflow import DAG
from airflow.configuration import conf
from airflow.utils import timezone
from airflow.utils.dates import days_ago
from ergo import SECTION_NAME
from ergo.operators.sqs.sqs_task_pusher import SqsTaskPusherOperator
from ergo.sensors.task_requests_batcher import TaskRequestBatchSensor

XCOM_REQUEST_TASK_KEY = "request.tasks"
TASK_ID_REQUEST_SENSOR = "collect_requests"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 10,
    'retry_delay': timedelta(minutes=2),
    'start_date': days_ago(1),
}

max_requests = conf.getint(SECTION_NAME, "max_task_requests", fallback=10)
sqs_queue_url = conf.get(SECTION_NAME, "request_queue_url")

with DAG(
    'ergo_task_queuer',
    default_args=default_args,
    is_paused_upon_creation=False,
    schedule_interval=timedelta(minutes=5),
    catchup=False,
    max_active_runs=1
) as dag:
    collector = TaskRequestBatchSensor(
        task_id=TASK_ID_REQUEST_SENSOR,
        max_requests=max_requests,
        xcom_tasks_key=XCOM_REQUEST_TASK_KEY
    )

    pusher = SqsTaskPusherOperator(
        task_id="push_tasks",
        task_id_collector=TASK_ID_REQUEST_SENSOR,
        xcom_tasks_key=XCOM_REQUEST_TASK_KEY,
        sqs_queue_url=sqs_queue_url
    )

collector >> pusher
