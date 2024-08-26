from datetime import datetime

import holidays
import requests
import time

from .diaries import authorization_l2, get_patients_from_table, get_pk, get_last_diaries, data_by_fields, \
    save_results, get_weekend_and_holidays, add_diaries, get_patient_pk, is_surgery_planned, get_all_records, \
    get_record_details
from utils.settings import login_l2, password_l2


def create_diaries_function():
    current_year = datetime.now().year
    holidays.country_holidays('RU', years=current_year)
    holidays_and_weekend = get_weekend_and_holidays(current_year)

    session = requests.Session()

    authorization_l2(session, login=login_l2, password=password_l2)

    patients = get_patients_from_table('C3:C42')
    patients_out_of_stock = get_patients_from_table('L3:L42')
    patients.extend(patients_out_of_stock)
    for history_number in patients:
        try:
            data = add_diaries(session, int(history_number), service_id=2)
            pk = data.get('pk')
            data_1 = get_pk(session, pk)
            date_str = data_1.get('direction').get('date')
            date_list = date_str.split('.')
            holidays_and_weekend_in_month = holidays_and_weekend.get(int(date_list[1]))

            weekday = datetime.strptime(date_str, '%d.%m.%Y')
            weekday_number = weekday.isoweekday()
            pk_1 = data_1.get('researches')[0].get('pk')
            data_2 = get_last_diaries(session, pk_1)
            pk_2 = data_2.get('data')[0].get('pk')
            local_status = data_by_fields(session, pk_2).get('data').get('1922')
            if date_list[0] in holidays_and_weekend_in_month:
                save_results(
                    connect=session,
                    pk=pk,
                    pk_2=pk_1,
                    local_status=local_status,
                    history_number=history_number,
                    what_inspection='дежурным травматологом-ортопедом'
                )
            elif weekday_number in (1, 5) and date_list[0] not in holidays_and_weekend_in_month:
                save_results(
                    connect=session,
                    pk=pk,
                    pk_2=pk_1,
                    local_status=local_status,
                    history_number=history_number,
                    what_inspection='лечащим врачом совместно с заведующим отделением'
                )
            else:
                save_results(
                    connect=session,
                    pk=pk,
                    pk_2=pk_1,
                    local_status=local_status,
                    history_number=history_number,
                    what_inspection='лечащим врачом'
                )
            time.sleep(2)

            """Добавляет протокол операции если стоит в плане операции"""
            patient_pk = get_patient_pk(session, '2872958')
            if is_surgery_planned(session, patient_pk).get('data'):
                add_diaries(session, history_number=int(history_number), service_id=5)

            """Добавляет диагностический эпикриз если его нет"""
            all_records = get_all_records(session, history_number=int(history_number))

            title_records = {}

            for item in all_records.get('data'):
                title_records[item.get('pk')] = item.get('researches')[0]

            diaries = []

            if 'Диагностический эпикриз' not in title_records.values():
                for key in title_records:
                    if title_records.get(key) == 'Осмотр':
                        diaries.append(key)

            title_examination = []
            for number in diaries:
                title_examination.append(get_record_details(session, number))

            if 'лечащим врачом совместно с заведующим отделением' in title_examination:
                add_diaries(session, service_id=20, history_number=int(history_number))
        except IndexError:
            pass
        except Exception as e:
            print(f'Error: {e}')
    session.close()
    return 'Дневники созданы'  # TypeError: object str can't be used in 'await' expression
