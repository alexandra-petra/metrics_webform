
import logging
from nicegui import ui
from calculate_metrics import calculate_metrics

logging.basicConfig(level=logging.INFO)



def submit_form():

    call_count_metrics_table.rows.clear()
    avg_call_duration_metrics_table.rows.clear()

    numbers_input = numbers_field.value
    start_date = start_date_field.value
    end_date = end_date_field.value
    
    if not numbers_input or not start_date or not end_date:
        ui.notify('All fields are required!', color='red')
        return


    try:
    
        list_of_numbers = [num.strip() for num in numbers_input.split(',')]
        # Validating if call count meets the threshold
        validate_call_count_threshold(list_of_numbers, start_date, end_date)
        
        metrics = calculate_metrics(list_of_numbers, start_date, end_date)
        
        call_count_metrics = metrics['call_count_metrics']
        avg_call_duration_metrics = metrics['avg_call_duration_metrics']



        call_count_metrics_table.rows.append({
            'type': 'доля отвеченных',
            'no_label': call_count_metrics[0],
            'label': call_count_metrics[1]
        })
        call_count_metrics_table.rows.append({
            'type': 'доля неотвеченных',
            'no_label': call_count_metrics[2],
            'label': call_count_metrics[3]
        })
        call_count_metrics_table.rows.append({
            'type': 'доля положивших трубку',
            'no_label': call_count_metrics[4],
            'label': call_count_metrics[5]
        })



        avg_call_duration_metrics_table.rows.append({
            'type': 'средняя длительность',
            'no_label': avg_call_duration_metrics[0],
            'label': avg_call_duration_metrics[1]
        })
        avg_call_duration_metrics_table.rows.append({
            'type': 'средняя длительность гудков',
            'no_label': avg_call_duration_metrics[2],
            'label': avg_call_duration_metrics[3]
        })



        call_count_metrics_table.update()
        avg_call_duration_metrics_table.update()

        

        ui.notify('Query executed successfully!', color='green')

    except Exception as e:
        ui.notify(f"Error occurred: {str(e)}", color='red')

ui.label('Call Metrics Dashboard').style('font-size: 24px; font-weight: bold; margin-bottom: 20px;')


with ui.card():
    ui.label('Input Parameters')
    numbers_field = ui.input('List of Numbers (comma-separated)', placeholder='e.g., 79658452027, 79658451998').style('width: 100%;')
    start_date_field = ui.input('Start Date', placeholder='YYYY-MM-DD').style('width: 100%;')
    end_date_field = ui.input('End Date', placeholder='YYYY-MM-DD').style('width: 100%;')
    ui.button('Submit', on_click=submit_form)

ui.label('Call Count Metrics').style('font-size: 20px; font-weight: bold; margin-top: 30px;')
call_count_metrics_table = ui.table(columns=[
    {'name': 'type', 'label': '', 'field': 'type'},
    {'name': 'no_label', 'label': 'Без Этикетки', 'field': 'no_label'},
    {'name': 'label', 'label': 'с Этикеткой', 'field': 'label'}
], rows=[]).style('margin-bottom: 30px;')

ui.label('Average Call Duration Metrics').style('font-size: 20px; font-weight: bold; margin-top: 30px;')
avg_call_duration_metrics_table = ui.table(columns=[
    {'name': 'type', 'label': '', 'field': 'type'},
    {'name': 'no_label', 'label': 'Без Этикетки', 'field': 'no_label'},
    {'name': 'label', 'label': 'с Этикеткой', 'field': 'label'}
], rows=[]).style('margin-bottom: 30px;')

ui.run(reconnect_timeout=120)
