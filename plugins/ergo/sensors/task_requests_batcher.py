from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.db import provide_session
from airflow.utils.decorators import apply_defaults
from airflow.utils.state import State

from ergo.models import ErgoTask


class TaskRequestBatchSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(
        self,
        max_requests: int,
        xcom_tasks_key: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.max_requests = max_requests
        self.xcom_tasks_key = xcom_tasks_key

    @provide_session
    def poke(self, context, session=None):
        result = session.query(ErgoTask).filter_by(
            state=State.QUEUED
        ).limit(self.max_requests)
        if result.count() < self.max_requests and context['ti'].is_eligible_to_retry():
            return False
        elif result:
            self.xcom_push(context, self.xcom_tasks_key, list(result))
            return True
        else:
            return False
