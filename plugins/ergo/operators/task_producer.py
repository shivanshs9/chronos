from airflow.contrib.hooks.aws_sqs_hook import SQSHook
from airflow.operators import BaseOperator
from airflow.utils.decorators import apply_defaults


class TaskProducerOperator(BaseOperator):
    @apply_defaults
    def __init__(
        self,
        task_id: str,
        task_data: dict,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
