import requests

BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/xd11bddxxpimt63p/'
GROUP_ID = 279  # ID вашей группы

# возвращает список ID задач с PARENT_ID = 0 для указанной группы
def get_tasks_by_group(group_id):
    url = f"{BITRIX24_WEBHOOK_URL}task.ctasks.getlist.json"
    params = {
        'filter[GROUP_ID]': group_id, 
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
        response_data = response.json()
        tasks = response_data.get('result', [])

        # Фильтруем задачи с PARENT_ID == 0 и GROUP_ID == нужному
        tasks_with_no_parent = [
            task['ID'] for task in tasks 
            if int(task.get('PARENT_ID', 0)) == 0 and int(task.get('GROUP_ID', 0)) == group_id
        ]
        
        return tasks_with_no_parent

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении задач: {e}")
        return []

if __name__ == "__main__":
    task_ids = get_tasks_by_group(GROUP_ID)
    print("Список ID задач с PARENT_ID = 0 для группы", GROUP_ID, ":", task_ids)