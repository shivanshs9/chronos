from airflow.plugins_manager import AirflowPlugin

from .operators.task_producer import TaskProducerOperator


class ErgoPlugin(AirflowPlugin):
    name = 'ergo'
    operators = (TaskProducerOperator,)
