import requests

# Ваш API ключ ClickUp
clickup_api_key = 'pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU'

# Получаем список команд
def get_clickup_teams():
    url = "https://api.clickup.com/api/v2/team"
    headers = {'Authorization': clickup_api_key}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Вызываем исключение для ошибки ответа

        if response.status_code == 200:
            teams = response.json().get('teams', [])
            if teams:
                for team in teams:
                    print(f"Team Name: {team['name']}, Team ID: {team['id']}")
            else:
                print("Не удалось найти команды.")
        else:
            print(f"Ошибка при получении команд: {response.status_code}")
            print(f"Ответ: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")

# Запуск функции
get_clickup_teams()
