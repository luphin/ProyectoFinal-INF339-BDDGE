from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 7, 4),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='generate_categorize_store_pipeline',
    default_args=default_args,
    description='Genera datos, los categoriza y guarda los no críticos',
    schedule_interval=None,  # Trigger manual
    catchup=False,
    tags=['example', 'data_pipeline'],
) as dag:

    generate_data = BashOperator(
        task_id='generate_data',
        bash_command='python3 /opt/airflow/scripts/random_data_generator.py --output file_path --output_path /opt/airflow/shared/output.json --num_records 10',
    )

    categorize_data = BashOperator(
        task_id='categorize_data',
        bash_command='python3 /opt/airflow/scripts/categorize.py',
    )

    store_non_critical = BashOperator(
        task_id='store_non_critical_data',
        bash_command='python3 /opt/airflow/scripts/store_non_critical.py',
    )

    generate_data >> categorize_data >> store_non_critical
