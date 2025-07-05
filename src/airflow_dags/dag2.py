from __future__ import annotations

import pendulum
import os
import json
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.apache.beam.operators.beam import BeamRunPythonPipelineOperator
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from kafka import KafkaProducer

CONTAINER_BASE_PATH = "/workspaces/ProyectoFinal-INF339-BDDGE/src/beam_pipelines"

def notify_kafka():
    producer = KafkaProducer(bootstrap_servers='kafka:19092',
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    message = {
        "event_type": "non_critical_data_stored",
        "data_entity": "FanEngagement",
        "status": "success",
        "location": "/output/",
        "processed_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "source_system": "generate_categorize_store_pipeline"
    }
    producer.send("fan-engagement-topic", message)
    producer.flush()

default_args = {
    'owner': 'airflow',
    'start_date': pendulum.datetime(2025, 7, 4, tz="UTC"),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='generate_categorize_store_pipeline',
    default_args=default_args,
    description='Genera datos, los categoriza y guarda los no críticos',
    schedule_interval=None,
    catchup=False,
    tags=['example', 'data_pipeline'],
) as dag:

    start = EmptyOperator(task_id="start")

    generate_data = BeamRunPythonPipelineOperator(
        task_id="generate_data",
        py_file=os.path.join(CONTAINER_BASE_PATH, "random_data_generator.py"),
        runner="DirectRunner",
        pipeline_options={
            "output": "file_path",
            "output_path": "output.json",
            "num_records": 10
        },
        env={"PYTHONPATH": "/workspaces/ProyectoFinal-INF339-BDDGE/src"}
    )


    categorize_data = BeamRunPythonPipelineOperator(
        task_id="categorize_data",
        py_file=os.path.join(CONTAINER_BASE_PATH, "categorize.py"),
        runner="DirectRunner",
        py_options=[],
        env={"PYTHONPATH": "/workspaces/ProyectoFinal-INF339-BDDGE/src"}
    )

    store_non_critical_data = BeamRunPythonPipelineOperator(
        task_id="store_non_critical_data",
        py_file=os.path.join(CONTAINER_BASE_PATH, "store_non_critical.py"),
        runner="DirectRunner",
        py_options=[],
        env={"PYTHONPATH": "/workspaces/ProyectoFinal-INF339-BDDGE/src"}
    )

    create_bucket = S3CreateBucketOperator(
        task_id="create_minio_bucket",
        aws_conn_id="minio-conn",
        bucket_name="my-bucket",
    )

    notify = PythonOperator(
        task_id="notify_kafka",
        python_callable=notify_kafka,
    )

    end = EmptyOperator(task_id="end")

    # Flujo
    (
        start
        >> generate_data
        >> categorize_data
        >> store_non_critical_data
        >> create_bucket
        >> notify
        >> end
    )
