import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.io.avroio import WriteToAvro
import json
import time
from datetime import datetime, timezone
import fastavro
import argparse
import logging
import os
from kafka import KafkaProducer

# Nuevos paths y esquemas
CRITICAL_AVRO_SCHEMA_PATH = 'resources/critical_schema.avsc'
NONCRITICAL_AVRO_SCHEMA_PATH = 'resources/non_critical_schema.avsc'
LOCAL_DATA_PATH = 'output.json'

CRITICAL_OUTPUT_DIR = 'output/criticos'
NONCRITICAL_OUTPUT_DIR = 'output/no_criticos'

def notify_kafka(topic, message):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send(topic, message.encode('utf-8'))
    producer.flush()
    producer.close()

class CategorizeFn(beam.DoFn):
    def process(self, element):
        record = json.loads(element)
        # Separar datos críticos y no críticos
        crit = record.copy()
        crit.pop('Implement', None)
        noncrit = record.get('Implement', None)
        if crit:
            yield beam.pvalue.TaggedOutput('critical', crit)
        if noncrit:
            yield beam.pvalue.TaggedOutput('noncritical', noncrit)

def main(argv=None, save_main_session=True):
    parser = argparse.ArgumentParser()
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session 

    # Cargar esquemas Avro
    critical_schema = fastavro.schema.load_schema(CRITICAL_AVRO_SCHEMA_PATH)
    noncritical_schema = fastavro.schema.load_schema(NONCRITICAL_AVRO_SCHEMA_PATH)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    critical_avro_path = os.path.join(CRITICAL_OUTPUT_DIR, f"criticos_{now}.avro")
    noncritical_avro_path = os.path.join(NONCRITICAL_OUTPUT_DIR, f"no_criticos_{now}.avro")

    with beam.Pipeline(options=pipeline_options) as p:
        categorized = (
            p
            | "Leer JSON" >> beam.io.ReadFromText(LOCAL_DATA_PATH)
            | "Categorizar" >> beam.ParDo(CategorizeFn()).with_outputs('critical', 'noncritical')
        )

        # Escribir críticos
        critical = categorized.critical
        critical | 'Write Critical Avro' >> WriteToAvro(
            critical_avro_path,
            schema=critical_schema,
            file_name_suffix='',
        )

        # Escribir no críticos
        noncritical = categorized.noncritical
        noncritical | 'Write NonCritical Avro' >> WriteToAvro(
            noncritical_avro_path,
            schema=noncritical_schema,
            file_name_suffix='',
        )

    # Notificar a Kafka después de la ejecución del pipeline
    if os.path.exists(critical_avro_path):
        notify_kafka("archivos_avro", f"Nuevo archivo crítico: {critical_avro_path}")
    if os.path.exists(noncritical_avro_path):
        notify_kafka("archivos_avro", f"Nuevo archivo no crítico: {noncritical_avro_path}")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
