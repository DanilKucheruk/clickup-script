import requests
import json

def get_task_details(task_id):
    url = "https://bit.paypoint.pro/rest/334/ns8ufic41u9h1nla/tasks.task.get"
    params = {
        "taskId": task_id  # ID задачи, которую нужно получить
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'result' in data and 'task' in data['result']:
            return data['result']['task']
        else:
            print("Ошибка: Неверный формат ответа")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None

def get_task_comments(task_id):
    url = "https://bit.paypoint.pro/rest/334/ns8ufic41u9h1nla/task.commentitem.getList"
    params = {"taskId": task_id}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'result' in data and isinstance(data['result'], list):
            return data['result']  # Просто возвращаем список комментариев
        else:
            print("Ошибка: Неверный формат ответа")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None



if __name__ == "__main__":
    task_id = 61945  # ID задачи
    task_details = get_task_details(task_id)
    task_comments = get_task_comments(task_id)
    
    if task_details:
        with open("task_63138.json", "w", encoding="utf-8") as file:
            json.dump(task_details, file, ensure_ascii=False, indent=4)
        print("Данные задачи сохранены в task_63138.json")
    
    if task_comments:
        with open("task_63138_comments.json", "w", encoding="utf-8") as file:
            json.dump(task_comments, file, ensure_ascii=False, indent=4)
        print("Комментарии сохранены в task_63138_comments.json")
