
FIELD_CATEGORY_ID = 'f842e5cd-3d36-4cf7-9b90-c9d12b398ae7'
FIELD_SIZE_ID = '8cae039c-7a32-4965-b868-e5412f3eacf9'
FIELD_BITRIX_LINK_ID = '03b28951-9048-46da-955b-dd383aaf5f3d'
BITRIX_TASK_URL_PREFIX = 'https://bit.paypoint.pro/workgroups/group/1/tasks/task/view/'
BITRIX_ID_CATEGORY_TO_CLICKUP_ID_CATEGORY = {
    '211': '23751d3d-d427-4be5-ba81-2cbc94dc68ed', # ❌ Баг
    '234': '8f235533-e32e-4330-9ac4-36d90b17324f',
    '229': '4d6cf26e-4912-42dd-af7b-87af918d3122',
    '236': '6d5999dd-cd16-4ed9-b23b-36a8f117e934',
    '208': 'c17d5377-4117-4f72-8c44-79aad234f608',
    '209': '315a1924-0ada-48c3-b0fb-56030ae3b19e',
    '215': 'daacaaf4-5f6e-44f6-a2b9-aa8ab6d5b914',
    '212': '8167c0f2-d16d-4f9c-8b37-149737d19bb1',
    '214': 'bc956cc8-0fef-4170-8bb2-6fbe5938eade',
    '233': '31e2cd64-fd20-48b3-91fb-4b8d5b0daf8c', # "Service / ⚕️ Исправление проблем, Сверки"
    '235': 'a6e69f0c-56a4-4770-8612-f1cb4bfa8611', # "Service / ⚖️ Исследование, Анализ, Архитектура"
    '213': '0d09d556-bef0-41a0-bd13-50069e565a8f', # "Service / #️⃣ Безопасность, доступы"
    '216': '10109d05-9828-45d3-83d4-439619894338', # "Service / ℹ️ Документация"
    '225': 'e4f7469f-6d98-40fa-a584-7920cd6cd21e', # "Service / ☕ Project Management"
    '218': '10b102b6-5258-40a2-8d87-9fa2569d33b8', # "Service / ☑️ Тестирование"
    '231': '9dca3bcc-8e31-447b-90a7-118e49ea9269', # "Service / ⚒️ Оборудование"
    '217': 'de00e22f-2315-4792-a499-4345dc41c9ec', # "Service / ⛄ Реальный мир, Офис, Поручение"
    '255': '6f1ba541-de06-4a04-bd4b-406bc7408b28', # "☢️ Подзадача для спама от бота"
    '257': '773338de-f96a-4c39-a493-adff081cd826', # "⛶ Группа задач"
    '223': '4e529397-28fd-40d7-87f3-4cf50902c456'  # "⭕ Прочее"
}

BITRIX_SIZE_TO_CLICKUP_SIZE = {
    '118' : 'ad1aca5d-f5cd-400d-bf46-c5746c81c84e',  # XS
    '119' : 'f8421ba8-6a33-45d6-a27f-90c841991179',  # S
    '120' : 'bbc2fae5-7b53-4eb1-8f34-74f3e67d9799',  # M
    '121' : '3caf6e70-c5c7-4ad3-bde8-f35fe4563136',  # L
    '122' : '8c52116e-4c27-4ba4-a571-cef1eb2289ce'   # XL
}

# Для обратной совместимости
BITRIX_ID_CATEGORY_TO_CLICKUP_ID_SIZE = BITRIX_SIZE_TO_CLICKUP_SIZE
BITRIX_ID_IMPORTANCE_TO_CLICKUP_PRIORITY = {
    '114': 1,  # High
    '115': 2,  # Normal
    '116': 3,  # Low
    '117': 4,  # Lowest
}


      
