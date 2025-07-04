import psycopg2
import json  # Importar la biblioteca JSON

def store_non_critical_data(non_critical_data):
    """
    Stores non-critical data into a PostgreSQL database.
    """
    # Configuración de conexión
    db_config = {
        "host": "localhost",
        "port": 5432,
        "dbname": "non_critical_data",
        "user": "postgres",
        "password": "password-root"
    }

    # Conexión a la base de datos
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # drop_query = "DROP TABLE IF EXISTS non_critical_data;"
        # cursor.execute(drop_query)
        # Crear tabla con estructura basada en el diccionario
        create_table_query = """
        CREATE TABLE IF NOT EXISTS non_critical_data (
            id SERIAL PRIMARY KEY,
            Implement_ID VARCHAR(50),
            Flow_Rate_L_min FLOAT,
            Soil_Temperature_C FLOAT,
            Nitrogen_ppm INT,
            Potassium_ppm INT,
            Phosphorus_ppm INT,
            Soil_Moisture_Percentage FLOAT,
            Yield_Mass_Flow_Rate_kg_s FLOAT,
            Yield_Rate_Per_Hectare_kg_ha FLOAT,
            Yield_Moisture_Content_Percentage FLOAT,
            Section1 VARCHAR(10),
            Section2 VARCHAR(10),
            Section3 VARCHAR(10),
            Seed_Rate_seeds_per_sq_m FLOAT
        );
        """
        cursor.execute(create_table_query)

        # Insertar datos no críticos
        insert_query = """
        INSERT INTO non_critical_data (
            Implement_ID, Flow_Rate_L_min, Soil_Temperature_C, Nitrogen_ppm, Potassium_ppm, Phosphorus_ppm,
            Soil_Moisture_Percentage, Yield_Mass_Flow_Rate_kg_s, Yield_Rate_Per_Hectare_kg_ha,
            Yield_Moisture_Content_Percentage, Section1, Section2, Section3, Seed_Rate_seeds_per_sq_m
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        for item in non_critical_data:
            # Extraer datos del diccionario
            data = (
                item["Implement_ID"],
                item["Flow_Rate_L_min"],
                item["Soil_Sensor_Data"]["Soil_Temperature_C"],
                item["Soil_Sensor_Data"]["Soil_Nutrient_Levels"]["Nitrogen_ppm"],
                item["Soil_Sensor_Data"]["Soil_Nutrient_Levels"]["Potassium_ppm"],
                item["Soil_Sensor_Data"]["Soil_Nutrient_Levels"]["Phosphorus_ppm"],
                item["Soil_Sensor_Data"]["Soil_Moisture_Percentage"],
                item["Yield_Monitor_Data"]["Yield_Mass_Flow_Rate_kg_s"],
                item["Yield_Monitor_Data"]["Yield_Rate_Per_Hectare_kg_ha"],
                item["Yield_Monitor_Data"]["Yield_Moisture_Content_Percentage"],
                item["Section_Control_Status"]["Section1"],
                item["Section_Control_Status"]["Section2"],
                item["Section_Control_Status"]["Section3"],
                item["Seed_Rate_seeds_per_sq_m"]
            )
            cursor.execute(insert_query, data)

        # Confirmar cambios
        conn.commit()
        print("Datos no críticos almacenados exitosamente.")

    except psycopg2.Error as e:
        print(f"Error al interactuar con la base de datos: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    from categorize import read_json_lines, categorize_items

    file_path = "output.json"
    json_data = read_json_lines(file_path)
    _, non_critical = categorize_items(json_data)

    store_non_critical_data(non_critical)