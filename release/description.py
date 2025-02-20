import bbcode
from markdownify import markdownify as md
import re
from get_link_to_image import get_link_to_image

def bbcode_to_markdown(bbcode_text):
    # Создаем парсер для BBCode
    parser = bbcode.Parser()

    def render_font(tag_name, value, options, parent, context):
        # Для monospace используем обратные кавычки
        if options and 'monospace' in str(options).lower():
            return f'{value}'
        return value
    
    # Регистрируем форматтеры
    parser.add_formatter('font', render_font)
    
    # Удаляем звездочки перед [SIZE] тегами
    bbcode_text = re.sub(r'\*\*\s*\[SIZE=', '[SIZE=', bbcode_text)
    
    # Преобразуем BBCode в HTML
    html_text = parser.format(bbcode_text)
    
    # Преобразуем HTML в Markdown
    markdown_text = md(html_text)
    
    # Обработка тега [SIZE] вручную
    markdown_text = handle_size_tags(markdown_text)

    markdown_text = handle_disk_file_tags(markdown_text)

    
    # Удаляем оставшиеся звездочки вокруг заголовков
    lines = markdown_text.split('\n')
    for i in range(len(lines)):
        if lines[i].lstrip().startswith('#'):
            # Удаляем звездочки в текущей строке
            lines[i] = lines[i].replace('**', '')
            # Если есть предыдущая строка, удаляем звездочки и в ней
            if i > 0:
                lines[i-1] = lines[i-1].replace('**', '')
    markdown_text = '\n'.join(lines)
    
    # Удаляем одиночные звездочки в начале строк
    markdown_text = re.sub(r'^\*\*\s*', '', markdown_text, flags=re.MULTILINE)
    
    # Ограничиваем количество переносов строк до двух
    markdown_text = re.sub(r'(\n\s*){3,}', '\n\n', markdown_text)
    
    return markdown_text

def handle_size_tags(text):
    """Обрабатываем теги [SIZE] и конвертируем в Markdown формат"""
    
    def size_replacement(match):
        size = match.group(1)
        content = match.group(2)
        
        # Удаляем звездочки вокруг заголовка
        content = content.replace('**', '')
        
        # Преобразуем размер в заголовок Markdown
        if size == "14pt":
            return f"\n## {content}"
        elif size == "15pt":
            return f"\n# {content}"
        elif size == "16pt":
            return f"\n# {content}"  # Для примера можно сделать больше
        # Для других размеров можно добавить дополнительные правила
        return content
    
    # Заменим теги [SIZE=xxpt] рекурсивно
    def replace_nested_size(text):
        while True:
            # Ищем только теги [SIZE] на внешнем уровне (не вложенные)
            match = re.search(r'\[SIZE=(\d+pt)\](.*?)\[/SIZE\]', text)
            if not match:
                break  # Выход из цикла, если не нашли тегов
            # Заменяем найденные теги
            text = re.sub(r'\[SIZE=(\d+pt)\](.*?)\[/SIZE\]', size_replacement, text)
        return text
    
    # Выполняем замену
    text = replace_nested_size(text)
    
    return text

def handle_disk_file_tags(text):
    """Обрабатываем теги [DISK FILE ID=n336759] и заменяем их на ссылки"""
    
    def disk_file_replacement(match):
        file_id = match.group(1)
        
        # Получаем реальную ссылку через API
        link = get_link_to_image(file_id)
        link = link.replace(" ", "%20")
        if link:
            return f"[Файл № {file_id}]({link})"
        else:
            return f"[Ошибка: файл не найден с ID {file_id}]"
    
    # Заменим все теги [DISK FILE ID=n...] на ссылку
    text = re.sub(r'\[DISK FILE ID=n(\d+)\]', disk_file_replacement, text)
    return text

def transfer_description(bitrix_task):
    task_id = bitrix_task.get('id', '')
    task_description = bitrix_task.get('description', '')
    task_bitrix = f'[Задача в Bitrix](https://bit.paypoint.pro/company/personal/user/334/tasks/task/view/{task_id}/)'

    task_description = task_bitrix + "\n" + bbcode_to_markdown(task_description)
    print("Преобразованное описание:")
    print(task_description)
    return task_description

