from datetime import datetime

NA = 'NA'


def gen_coord(lat=None, lon=None):
    """
    NMEA 0183 coordinates encoder
    """
    if not lat or not lon:
        return 'NA;NA;NA;NA'
    try:
        litLat, litLon = 'N', 'E'
        if lat < 0:
            lat = abs(lat)
            litLat = 'S'
        if lon < 0:
            lon = abs(lon)
            litLon = 'W'
        result = f'{lat//1:02.0f}{lat%1*60:07.4f};{litLat};{lon//1:03.0f}{lon%1*60:07.4f};{litLon}'
    except:
        result = 'NA;NA;NA;NA'
    return result


def gen_ADC(ports_dict):
    """
    Аналоговые входы. Дробные числа, через запятую. Нумерация датчика начинается с единицы.
    Если аналоговые входы отсутствуют, передается NA.
    Пример: 14.77,0.02,3.6
    """
    if ports_dict == NA:
        return ports_dict
    result = []
    try:
        for port in sorted(filter(lambda x: x[0] == 'a', ports_dict)):
            result.append(f'{ports_dict.get(port)/1000:.3f}') if ports_dict.get(port) else result.append('0.0')
        result = ','.join(result) if result else NA
    except Exception as e:
        print("gen_ADC>", e)
        result = NA
    return result


def gen_digits_inputs(ports_dict):
    """
    Цифровые входы. Каждый бит числа соответствует одному входу, начиная с младшего.
    Целое число. Если отсутствует, передается NA
    """
    if ports_dict == NA:
        return ports_dict
    result = []
    try:
        for port in sorted(filter(lambda x: x[0] == 'd', ports_dict), reverse=True):
            result.append(f'{ports_dict.get(port):1d}')
        result = int(''.join(result), 2) if result else NA
    except Exception as e:
        print(e)
        result = NA
    return result


def gen_params(data):
    params = []
    try:
        params.append(f"status:1:{data.get('STATUS')}") if data.get('STATUS') else None
        params.append(f"pwr_ext:2:{data.get('U')/1000:.3f}") if data.get('U') else None
        params.append(f"pwr_int:2:{data.get('U_BAT')/1000:.3f}") if data.get('U_BAT') else None
        # params.append(f"SOS:1:{int(data.get('ALARM'))}") if data.get('ALARM') is not None else None
        params.append(f"mileage:2:{data.get('MILEAGE')}") if data.get('MILEAGE') else None
        params.append(f"engine:1:{int(data.get('ENGINE'))}") if data.get('ENGINE') is not None else None
        params.append(f"jam:1:{data.get('JAMM'):1d}") if data.get('JAMM') is not None else None
        for i, port in enumerate(sorted(filter(lambda x: x[:2] == 'rs', data.get('INPUTS', {})))):
            params.append(f"rs485fuel_level{i+1}:1:{data['INPUTS'].get(port) * 10}")
        params = ','.join(params)
    except:
        return NA
    return params



def gen_string(data:dict):

    dt_object = datetime.fromtimestamp(data.get('TIMESTAMP', 0))
    coords = gen_coord(data.get('LATITUDE'), data.get('LONGITUDE'))
    # Outputs, ibotton = NA
    inputs = data.get('INPUTS', NA)
    encoded_string = f"#D#{dt_object:%d%m%y;%H%M%S};" \
                     f"{coords};" \
                     f"{data.get('SPEED', NA)};" \
                     f"{data.get('COURSE', NA)};" \
                     f"{data.get('ALTITUDE', NA)};" \
                     f"{data.get('SATELLITES', NA)};" \
                     f"{data.get('HDOP', NA)};NA;" \
                     f"{gen_digits_inputs(inputs)};" \
                     f"NA;" \
                     f"{gen_ADC(inputs)};" \
                     f"NA;" \
                     f"{gen_params(data)};"
    return encoded_string



if __name__ == '__main__':
    # '#D#date;time;lat1;lat2;lon1;lon2;speed;course;height;sats;hdop;inputs;outputs;adc;ibutton;params'

    example_dict = {
        "OBJID": 31835597,
        "TIMESTAMP": 1643307381,
        "LATITUDE": 57.928123474121094,
        "LONGITUDE": 40.00664138793945,
        "ALTITUDE": 133,
        "COURSE": 359,
        "SPEED": 86,
        "U": 28583,
        "U_BAT": 149,
        "SATELLITES": 17,
        "ALARM": 1,
        "HDOP": 6,
        "STATUS": 4096,
        "INPUTS": {
            "a1": 7555, "a2": 0, "a3": 0, "a4": 0, "a5": 0, "a6": 0, "d1": 0, "d2": True, "c1": 0, "c2": 0, "rs1": 0, "rs2": 0, "rs3": 249,
                "rs1_t": 0, "rs2_t": 0, "rs3_t": -1
        },
    }
    outString = gen_string(example_dict)
    print(outString)
