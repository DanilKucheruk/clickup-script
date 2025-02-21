import requests

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_map_category_and_priority import BITRIX_ID_CATEGORY_TO_CLICKUP_ID_CATEGORY, FIELD_ID
from get_task_category import get_task_importance, get_task_category

def set_custom_field(clickup_task_id, bitrix_task_id):
    try:
        url = f"https://api.clickup.com/api/v2/task/{clickup_task_id}/field/{FIELD_ID}"
        headers = {
            "Authorization": "pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU",
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        # Получаем категорию из Bitrix по ID задачи Bitrix
        bitrix_category_id = get_task_category(bitrix_task_id)
        if not bitrix_category_id:
            print(f"⚠️ Не удалось получить категорию для задачи Bitrix {bitrix_task_id}")
            return
            
        # Конвертируем ID категории Bitrix в ID категории ClickUp
        if bitrix_category_id not in BITRIX_ID_CATEGORY_TO_CLICKUP_ID_CATEGORY:
            print(f"⚠️ Категория Bitrix {bitrix_category_id} не найдена в маппинге")
            return
            
        clickup_category_id = BITRIX_ID_CATEGORY_TO_CLICKUP_ID_CATEGORY[bitrix_category_id]
        data = {
            "value": clickup_category_id
        }

        # Отправляем запрос в ClickUp
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if 'error' in result:
            print(f"⚠️ Ошибка при установке категории: {result['error']}")
        else:
            print(f"✅ Категория успешно установлена для задачи {clickup_task_id}")
            
    except Exception as e:
        print(f"❌ Ошибка при установке категории: {str(e)}")
