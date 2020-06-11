from datetime import datetime

from sqlalchemy import (Column, ForeignKey, ForeignKeyConstraint, Index,
                        Integer, String, Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from airflow.models import TaskInstance
from airflow.models.base import ID_LEN
from airflow.utils import timezone
from airflow.utils.sqlalchemy import UtcDateTime
from airflow.utils.state import State

from ergo import JobResultStatus

Base = declarative_base()

class ErgoTask(Base):
    __tablename__ = 'ergo_task'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(128), nullable=False)
    request_data = Column(Text, nullable=True)
    # state transitions: SCHEDULED -> QUEUED -> RUNNING -> SUCCESS
    state = Column(String(20), default=State.SCHEDULED, nullable=False) # enum{State}
    created_at = Column(
        UtcDateTime, index=True, default=timezone.utcnow, nullable=False
    )
    updated_at = Column(
        UtcDateTime, index=True, nullable=False,
        default=timezone.utcnow, onupdate=timezone.utcnow
    )
    ti_task_id = Column(String(ID_LEN), nullable=False)
    ti_dag_id = Column(String(ID_LEN), nullable=False)
    ti_execution_date = Column(UtcDateTime, nullable=False)

    job = relationship('ErgoJob', back_populates='task')
    # task_instance = relationship('TaskInstance')

    __table_args__ = (
        ForeignKeyConstraint(
            (ti_task_id, ti_dag_id, ti_execution_date),
            (TaskInstance.task_id, TaskInstance.dag_id, TaskInstance.execution_date),
            ondelete='CASCADE'
        ),
    )

    def __str__(self):
        return f'#{self.id}: {self.task_id}'

    def __init__(self, task_id, ti, request_data=''):
        self.task_id = task_id
        self.ti_task_id = ti.task_id
        self.ti_dag_id = ti.dag_id
        self.ti_execution_date = ti.execution_date
        self.request_data = request_data

class ErgoJob(Base):
    __tablename__ = 'ergo_job'

    id = Column(String(128), primary_key=True)
    task_id = Column(
        ForeignKey("ergo_task.id", ondelete='CASCADE'),
        nullable=False,
        index=True,
        unique=True
    )
    result_data = Column(Text, nullable=True)
    result_code = Column(Integer, default=JobResultStatus.NONE, nullable=False)  # enum{JobResultStatus}
    error_msg = Column(Text, nullable=True)
    # TODO: other metadata?

    task = relationship('ErgoTask', back_populates='job')

    def __init__(self, job_id, task, result=None):
        self.id = job_id
        self.task_id = task.id
        if result is not None:
            # TODO: Parse result and fill
            pass
