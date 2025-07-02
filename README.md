# ProyectoFinal-INF339-BDDGE

ProyectoFinal INF339

## Integrantes

1. Diego Moyano 202004509-7
2. Luis Zegarra 202073628-6
3. Nicolas Cancino 202004680-8

## Actividades

Sistemas fuente:
    1. Vehículos
    2. Implementos Agrícolas
Serialización:
    Se usara serialización de tipo Avro para recibir los datos ya que es más eficiente y adecuado para sistemas distribuidos en producción.
Ingesta de datos:
    1. Para los vehículos se utilizará una ingesta en tiempo real debido a la criticidad de los datos transmitidos.
    2. Para los Implementos agrícolas se utilizará carga por lotes, ya que son datos de gran volumen que se recopilan, comprimen y se cargan diariamente, pero no son de gran urgencia.
Transformación:
    Por verse
Servir los datos:
    Para servir los datos se entregará una API al usuario para que pueda hacer consultas.
    También se entregarán los datos a un procesado de análisis predictivo.
Seguridad:
    durante el transito de los datos se cifrarán con Cifrado TLD/SSL
    y en reposo estarán cifrados con Cifrado AES-256