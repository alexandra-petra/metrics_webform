
import logging
import clickhouse_connect
from credentials import host, port, username, password, database

# Initializing the client
client = clickhouse_connect.get_client(host=host, 
                                       port=port, 
                                       username=username, 
                                       password=password, 
                                       database=database
                                       )

def execute_query(query):
    """
    Function for query execution and for the logging and errors handling.
    """
    try:
        logging.info(f"Executing query: {query}")
        result = client.query(query).result_rows
        logging.info(f"Query result: {result}")
        return result[0] if result else []
    except Exception as e:
        logging.error(f"Error during query execution: {e}")
        raise
        
        
def validate_call_count_threshold(numbers, start_date, end_date, threshold=100):
    """
    Checks if the number of calls meets the required threshold.
    """
    formatted_numbers = ', '.join([f"'{num.strip()}'" for num in numbers])
    query = f"""
    SELECT COUNT(call_start_time) AS call_count
    FROM default.LABEL_CDR_V_2_0
    WHERE a_number IN ({formatted_numbers})
    AND toDate(call_start_time) >= '{start_date}'
    AND toDate(call_start_time) < '{end_date}'
    """
    call_count = execute_query(query)
    if call_count < threshold:
        raise ValueError(f"Too few calls were made for valid statistics! More than {threshold} calls is required.")



def calculate_call_count_metrics(numbers, start_date, end_date):
    """
    Calculate metrics related to call counts.
    """
    formatted_numbers = ', '.join([f"'{num.strip()}'" for num in numbers])
    query = f"""
    SELECT
        ROUND(SUM(CASE WHEN talk_duration > 0 THEN 1 ELSE 0 END) / COUNT(call_start_time), 4) AS dolya_otvechennych_no_lbl,
        ROUND(SUM(CASE WHEN feature_code = 'LABELB' AND talk_duration > 0 THEN 1 ELSE 0 END) / SUM(CASE WHEN feature_code = 'LABELB' THEN 1 ELSE 0 END), 4) AS dolya_otvechennych_lbl,
        ROUND(SUM(CASE WHEN talk_duration = 0 THEN 1 ELSE 0 END) / COUNT(call_start_time), 4) AS dolya_neotvechennych_no_lbl,
        ROUND(SUM(CASE WHEN feature_code = 'LABELB' AND talk_duration = 0 THEN 1 ELSE 0 END) / SUM(CASE WHEN feature_code = 'LABELB' THEN 1 ELSE 0 END), 4) AS dolya_neotvechennych_lbl,
        ROUND(SUM(CASE WHEN terminating_party = 't' THEN 1 ELSE 0 END) / COUNT(call_start_time), 4) AS dolya_polozhil_trubku_b_no_lbl,
        ROUND(SUM(CASE WHEN feature_code = 'LABELB' AND terminating_party = 't' THEN 1 ELSE 0 END) / SUM(CASE WHEN feature_code = 'LABELB' THEN 1 ELSE 0 END), 4) AS dolya_polozhil_trubku_b_lbl
    FROM default.LABEL_CDR_V_2_0
    WHERE a_number IN ({formatted_numbers})
    AND toDate(call_start_time) >= '{start_date}'
    AND toDate(call_start_time) < '{end_date}'
    """
    return execute_query(query)

def calculate_avg_call_duration_metrics(numbers, start_date, end_date):
    """
    Calculate metrics related to average call duration.
    """
    formatted_numbers = ', '.join([f"'{num.strip()}'" for num in numbers])
    query = f"""
    SELECT
        ROUND(AVG(CASE WHEN feature_code <> 'LABELB' OR feature_code IS NULL THEN talk_duration END), 1) AS srednaya_dlit_no_lbl,
        ROUND(AVG(CASE WHEN feature_code = 'LABELB' THEN talk_duration END), 1) AS srednaya_dlit_lbl,
        ROUND(AVG(CASE WHEN feature_code != 'LABELB' THEN (call_duration - talk_duration) END), 1) AS srednaya_dlit_gudkov_no_lbl,
        ROUND(AVG(CASE WHEN feature_code = 'LABELB' THEN (call_duration - talk_duration) END), 1) AS srednaya_dlit_gudkov_lbl
    FROM default.LABEL_CDR_V_2_0
    WHERE a_number IN ({formatted_numbers})
    AND toDate(call_start_time) >= '{start_date}'
    AND toDate(call_start_time) < '{end_date}'
    """
    return execute_query(query)

def calculate_metrics(numbers, start_date, end_date):
    """
    Wrapper function to calculate all metrics.
    """
    return {
        'call_count_metrics': calculate_call_count_metrics(numbers, start_date, end_date),
        'avg_call_duration_metrics': calculate_avg_call_duration_metrics(numbers, start_date, end_date),
    }
