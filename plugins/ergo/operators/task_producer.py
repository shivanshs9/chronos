import json

from airflow.contrib.hooks.aws_sqs_hook import SQSHook
from airflow.operators import BaseOperator
from airflow.utils.db import provide_session
from airflow.utils.decorators import apply_defaults
from ergo.models import ErgoTask


class ErgoTaskProducerOperator(BaseOperator):
    @apply_defaults
    def __init__(
        self,
        ergo_task_id: str,
        ergo_task_data: dict = {},
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.ergo_task_id = ergo_task_id
        self.ergo_task_data = ergo_task_data

    @provide_session
    def execute(self, context, session=None):
        ti = context['ti']
        req_data = json.dumps(self.ergo_task_data) if self.ergo_task_data is not None else ''
        task = ErgoTask(self.ergo_task_id, ti, req_data)
        session.add(task)
        session.commit()
