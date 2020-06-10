from airflow.contrib.hooks.aws_sqs_hook import SQSHook
from airflow.operators import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.session import provide_session
from airflow.utils.state import State

from ...models import ErgoJob, ErgoTask


class SqsTaskPusherOperator(BaseOperator):
    @apply_defaults
    def __init__(
        self,
        task_id_collector: str,
        xcom_tasks_key: str,
        sqs_queue_url: str,
        aws_conn_id='aws_default',
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.task_id_collector = task_id_collector
        self.xcom_tasks_key = xcom_tasks_key
        self.sqs_queue_url = sqs_queue_url
        self.aws_conn_id = aws_conn_id

    @provide_session
    def execute(self, context, session=None):
        dag_id = context['ti'].dag_id
        tasks = self.xcom_pull(context, self.task_id_collector, dag_id, self.xcom_tasks_key)
        sqs_client = SQSHook(aws_conn_id=self.aws_conn_id).get_conn()
        self.log.info('SqsTaskPusherOperator trying to push %d messages on queue: %s', len(tasks), self.sqs_queue_url)
        entries = [
            {
                'Id': task.id,
                'MessageBody': task.request_data,
                'MessageGroupId': task.task_id
            }
            for task in tasks
        ]
        response = sqs_client.send_message_batch(
            QueueUrl=self.sqs_queue_url,
            Entries=entries
        )
        success_resps = response.get('Successful', list())
        failed_resps = response.get('Failed', list())
        if success_resps:
            self.log.info('SqsTaskPusherOperator successfully pushed %d messages!', len(success_resps))
            task_mappings = [
                {
                    ErgoTask.id: resp['Id'],
                    ErgoTask.state: State.SCHEDULED
                }
                for resp in success_resps
            ]
            session.bulk_update_mappings(ErgoTask, task_mappings)
            job_mappings = [
                {
                    ErgoJob.id: resp['MessageId'],
                    ErgoJob.task_id: resp['Id']
                }
                for resp in success_resps
            ]
            session.bulk_insert_mappings(ErgoJob, job_mappings)
        if failed_resps:
            self.log.error('SqsTaskPusherOperator failed to push %d messages!', len(failed_resps))
            task_mappings = [
                {
                    ErgoTask.id: resp['Id'],
                    ErgoTask.state: State.UP_FOR_RETRY
                }
                for resp in failed_resps
            ]
            session.bulk_update_mappings(ErgoTask, task_mappings)
