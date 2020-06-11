from sqlalchemy.orm import joinedload

from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.db import provide_session
from airflow.utils.decorators import apply_defaults
from airflow.utils.state import State
from ergo.models import ErgoJob, ErgoTask


class ErgoJobResultSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(
        self,
        ergo_task_id: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.ergo_task_id = ergo_task_id
    
    @provide_session
    def poke(self, context, session=None):
        ti = context['ti']
        tasks = (
            session.query(ErgoTask)
            .options(joinedload('job'))
            .filter_by(task_id=self.ergo_task_id, ti_dag_id=ti.dag_id)
        )
        self.log.info('Received %d results...', len(tasks))
        for task in tasks:
            job = task.job
            if job is None or task.state in State.unfinished():
                return False
        return True
