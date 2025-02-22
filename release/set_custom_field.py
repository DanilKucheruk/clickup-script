import requests

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_map_category_and_priority import (
    BITRIX_ID_CATEGORY_TO_CLICKUP_ID_CATEGORY,
    BITRIX_SIZE_TO_CLICKUP_SIZE,
    FIELD_CATEGORY_ID,
    FIELD_SIZE_ID,
    FIELD_BITRIX_LINK_ID,
    BITRIX_TASK_URL_PREFIX
)
from get_task_category import get_task_importance, get_task_category, get_task_size

def set_custom_fields(clickup_task_id, bitrix_task_id):
    success = True
    headers = {
        "Authorization": "pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU",
        "accept": "application/json",
        "content-type": "application/json"
    }
    
    try:
        # Установка категории
        bitrix_category_id = get_task_category(bitrix_task_id)
        if not bitrix_category_id:
            print(f"⚠️ Не удалось получить категорию для задачи Bitrix {bitrix_task_id}")
        elif bitrix_category_id not in BITRIX_ID_CATEGORY_TO_CLICKUP_ID_CATEGORY:
            print(f"⚠️ Категория Bitrix {bitrix_category_id} не найдена в маппинге")
        else:
            clickup_category_id = BITRIX_ID_CATEGORY_TO_CLICKUP_ID_CATEGORY[bitrix_category_id]
            url = f"https://api.clickup.com/api/v2/task/{clickup_task_id}/field/{FIELD_CATEGORY_ID}"
            response = requests.post(url, headers=headers, json={"value": clickup_category_id})
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                print(f"⚠️ Ошибка при установке категории: {result['error']}")
                success = False
            else:
                print(f"✅ Категория успешно установлена для задачи {clickup_task_id}")
        
        # Установка размера
        bitrix_size_id = get_task_size(bitrix_task_id)
        if not bitrix_size_id:
            print(f"ℹ️ Размер не установлен: не найден размер в Bitrix для задачи {bitrix_task_id}")
        elif bitrix_size_id not in BITRIX_SIZE_TO_CLICKUP_SIZE:
            print(f"⚠️ Размер Bitrix {bitrix_size_id} не найден в маппинге")
        else:
            clickup_size_id = BITRIX_SIZE_TO_CLICKUP_SIZE[bitrix_size_id]
            url = f"https://api.clickup.com/api/v2/task/{clickup_task_id}/field/{FIELD_SIZE_ID}"
            response = requests.post(url, headers=headers, json={"value": clickup_size_id})
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                print(f"⚠️ Ошибка при установке размера: {result['error']}")
                success = False
            else:
                print(f"✅ Размер задачи успешно установлен для задачи {clickup_task_id}")
        
        # Установка ссылки на Bitrix задачу
        bitrix_url = f"{BITRIX_TASK_URL_PREFIX}{bitrix_task_id}/"
        url = f"https://api.clickup.com/api/v2/task/{clickup_task_id}/field/{FIELD_BITRIX_LINK_ID}"
        response = requests.post(url, headers=headers, json={"value": bitrix_url})
        response.raise_for_status()
        result = response.json()
        
        if 'error' in result:
            print(f"⚠️ Ошибка при установке ссылки на Bitrix: {result['error']}")
            success = False
        else:
            print(f"✅ Ссылка на Bitrix задачу успешно установлена для задачи {clickup_task_id}")
                    
    except Exception as e:
        print(f"❌ Ошибка при установке полей: {str(e)}")
        success = False
        
    return success

# Для обратной совместимости
def set_custom_field(clickup_task_id, bitrix_task_id):
    return set_custom_fields(clickup_task_id, bitrix_task_id)
