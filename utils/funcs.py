import json


def get_data() -> tuple[list[dict], list[dict], list[dict]]:
    """
    Загружает данные из файла
    :return: tuple
    """
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    office_list = []
    department_list = []
    employee_list = []
    for item in data:
        if item.get('Type') == 1:
            office_list.append(item)
        elif item.get('Type') == 2:
            department_list.append(item)
        elif item.get('Type') == 3:
            employee_list.append(item)

    return office_list, department_list, employee_list
