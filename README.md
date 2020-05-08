## Chronos (Provisional Name)
#### Cron Scheduler powered by Airflow

### How to run
- Run `docker-compose up --build`
- Navigate to http://localhost:8080/admin/connection/ once it runs successfully
- Edit connection with conn ID = "aws_default":
    - Host: http://sqs:9324
    - Login: \<AWSAccessKeyId>
    - Password: \<AWSSecretAccessKey>
    - Extra - ```{
        "host": "http://sqs:9324",
        "region_name": "default"
        }```
- Navigate to DAG View and enable "example_sqs" DAG.