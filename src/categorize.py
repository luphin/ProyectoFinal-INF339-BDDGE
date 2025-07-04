import json

def read_json_lines(file_path):
    """
    Reads a file where each line is a JSON object and returns a list of parsed JSON objects.
    """
    json_objects = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    json_objects.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    return json_objects


def categorize_items(json_data):
    """
    Categorizes JSON objects into 'Critical' and 'Non-Critical' based on their 'type' field.
    """
    critical = []
    non_critical = []

    for item in json_data:
        critical.append({
        'Vehicle_ID': item.get('Vehicle_ID'),
        'Timestamp': item.get('Timestamp'),
        'GPS_Coordinates': item.get('GPS_Coordinates'),
        'Engine_RPM': item.get('Engine_RPM'),
        'Engine_Load_Percentage': item.get('Engine_Load_Percentage'),
        'Fuel_Level_Percentage': item.get('Fuel_Level_Percentage'),
        'Fuel_Consumption_Rate_L_hr': item.get('Fuel_Consumption_Rate_L_hr'),
        'Speed_km_h': item.get('Speed_km_h'),
        'Odometer_km': item.get('Odometer_km'),
        'Operating_Hours': item.get('Operating_Hours'),
        'Hydraulic_Pressure_psi': item.get('Hydraulic_Pressure_psi'),
        'Hydraulic_Fluid_Temp_C': item.get('Hydraulic_Fluid_Temp_C'),
        'Engine_Coolant_Temp_C': item.get('Engine_Coolant_Temp_C'),
        'Battery_Voltage_V': item.get('Battery_Voltage_V'),
        'Gear_Engaged': item.get('Gear_Engaged'),
        'Accelerator_Pedal_Position_Percentage': item.get('Accelerator_Pedal_Position_Percentage'),
        'Brake_Pedal_Position_Percentage': item.get('Brake_Pedal_Position_Percentage'),
        'Diagnostic_Data': item.get('Diagnostic_Data'),
        })
        non_critical.append(item.get('Implement', {}))

    return critical, non_critical


if __name__ == "__main__":
    file_path = "output.json"
    json_data = read_json_lines(file_path)
    critical, non_critical = categorize_items(json_data)

    print("Critical items:")
    print(critical)
    print("Non-critical items:")
    print(non_critical)