from __future__ import annotations

import pendulum

from airflow.operators.empty import EmptyOperator
from airflow.providers.apache.beam.operators.beam import BeamRunPythonPipelineOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from kafka import KafkaProducer
import json

CONTAINER_BASE_PATH = "/workspaces/ProyectoFinal-INF339-BDDGE"
BEAM_PIPELINE_PY_PATH = "src/beam_pipelines/main.py"
BEAM_PIPELINE_PATH = os.path.join(CONTAINER_BASE_PATH, BEAM_PIPELINE_PY_PATH)

def notify_kafka():
    producer = KafkaProducer(bootstrap_servers='kafka:19092',
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    message = {
        "event_type": "data_processing_completed",
        "data_entity": "FanEngagement",
        "status": "success",
        "location": "/output/outuput.json",
        "processed_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "source_system": "dag1"
    }
    producer.send("fan-engagement-topic", message)
    producer.flush()

with DAG(
    "run_beam_dag",
    description="A simple DAG to demonstrate basic Airflow functionality",
    schedule="@daily",
    start_date=pendulum.datetime(2025, 6, 1, tz="UTC"),
    catchup=False,
    tags=["example", "simple_dag"],
) as dag:
    first_step = EmptyOperator(task_id="First_step")
    start_python_pipeline_local_direct_runner = BeamRunPythonPipelineOperator(
        task_id="start_python_pipeline_local_direct_runner",
        py_file=BEAM_PIPELINE_PATH,
        #py_options=["-m"],
        runner="DirectRunner",
        #py_requirements=["apache-beam[gcp]==2.65.0"],
        #py_interpreter="python3",
        #py_system_site_packages=False,
    )
    bucket_name = "my-bucket"
    bucket_creation = S3CreateBucketOperator(
        task_id="create_bucket",
        aws_conn_id="minio-conn",
        bucket_name=bucket_name,
    )
    TEMP_FILE_PATH = "/workspaces/ProyectoFinal-INF339_BDDGE/output/ouput.json"
    create_local_to_s3_job = LocalFilesystemToS3Operator(
        task_id="create_local_to_s3_job",
        aws_conn_id="minio-conn",
        filename=TEMP_FILE_PATH,
        dest_key=f"s3://{bucket_name}/s3_key/processed_data.parquet",
        replace=True,
    )
    end_step = EmptyOperator(task_id="End_step")

    notify = PythonOperator(
        task_id="notify_kafka",
        python_callable=notify_kafka
    )

    first_step >> start_python_pipeline_local_direct_runner >> bucket_creation >> create_local_to_s3_job >> end_step >> notify