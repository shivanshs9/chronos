# Dummy file to load required dags from ergo
from airflow import DAG
from ergo.dags.dag_task_queuer import dag as sqs_queue_dag
