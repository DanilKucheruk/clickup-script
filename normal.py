import requests
import json

API_TOKEN = "pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU"

TASK_ID = "8697za87j"

URL = f"https://api.clickup.com/api/v2/task/{TASK_ID}/checklist"


HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

CHECKLIST_DATA = {
    "name": "Чек-лист 1",
    "items": [
        {
            "name": "1 fdsafdsafsd",
            "children": [
                {
                    "name": "1.1 dsfda",
                    "children": [
                        {
                            "name": "1.1.1 332132"
                        }
                    ]
                }
            ]
        }
    ]
}

response = requests.post(URL, headers=HEADERS, data=json.dumps(CHECKLIST_DATA))

if response.status_code == 200:
    print("Чек-лист успешно добавлен в задачу!")
else:
    print(f"Ошибка {response.status_code}: {response.text}")
