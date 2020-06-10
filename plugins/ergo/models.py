from datetime import datetime

from sqlalchemy import Column, ForeignKey, Index, Integer, String, Text

from airflow.models.base import Base
from airflow.utils import timezone
from airflow.utils.sqlalchemy import UtcDateTime
from airflow.utils.state import State


class ErgoTask(Base):
    __tablename__ = 'ergo_task'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(128), nullable=False)
    request_data = Column(Text, nullable=True)
    state = Column(String(20), default=State.QUEUED, nullable=False)
    created_at = Column(
        UtcDateTime, index=True, default=timezone.utcnow, nullable=False
    )
    updated_at = Column(
        UtcDateTime, index=True, nullable=False,
        default=timezone.utcnow, onupdate=timezone.utcnow
    )

    __table_args__ = {
        'extend_existing': True
    }

    def __str__(self):
        return f'#{self.id}: {self.task_id}'


class ErgoJob(Base):
    __tablename__ = 'ergo_job'

    id = Column(String(128), primary_key=True)
    task_id = Column(
        ForeignKey("ergo_task.id", ondelete='CASCADE'),
        nullable=False,
        index=True,
        unique=True
    )
    # TODO: other metadata (results, etc)

    __table_args__ = {
        'extend_existing': True
    }
