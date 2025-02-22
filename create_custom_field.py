import requests
from config_map_category_and_priority import BITRIX_ID_CATEGORY_TO_CLICKUP_ID_CATEGORY

# ClickUp API configuration
CLICKUP_API_KEY = 'pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU'
CLICKUP_LIST_ID = '901508672918'

def create_category_field():
    """Create a custom Category field in ClickUp with dropdown options"""
    
    url = f'https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/field'
    headers = {
        'Authorization': CLICKUP_API_KEY,
        'Content-Type': 'application/json'
    }

    # Get unique category names and their IDs
    options = []
    for bitrix_id, clickup_id in BITRIX_ID_CATEGORY_TO_CLICKUP_ID_CATEGORY.items():
        # Extract category name from the comment in config file
        # Get the mapping value and check if it has a comment
        mapping_value = BITRIX_ID_CATEGORY_TO_CLICKUP_ID_CATEGORY.get(bitrix_id, '')
        if isinstance(mapping_value, str) and '#' in mapping_value:
            # Extract the name from the comment, e.g., "value, # Name" -> "Name"
            category_name = mapping_value.split('#', 1)[1].strip()
        else:
            category_name = f"Category {bitrix_id}"
        
        options.append({
            "name": category_name,
            "id": clickup_id
        })

    # Field configuration
    data = {
        "name": "Category",
        "type": "drop_down",
        "required": False,
        "type_config": {
            "default": None,
            "placeholder": None,
            "options": options
        }
    }

    try:
        import json
        print("Request payload:")
        print(json.dumps(data, indent=2))
        
        response = requests.post(url, headers=headers, json=data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        result = response.json()
        
        if response.status_code == 200:
            field_id = result['field']['id']
            print(f"✅ Custom field 'Category' created successfully with ID: {field_id}")
            print("Update the FIELD_ID in config_map_category_and_priority.py with this value")
            print("\nNew option IDs mapping:")
            print("{")
            for option in result["field"]["type_config"]["options"]:
                print(f"    '{option['name'].split()[-1]}': '{option['id']}',  # {option['name']}")
            print("}")
            return field_id
        else:
            print(f"❌ Error creating custom field: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating custom field: {str(e)}")
        return None

if __name__ == "__main__":
    create_category_field()
