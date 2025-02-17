import re

def preserve_bold(text):
    # Remove all formatting
    text = re.sub(r'\[/?[A-Z]+[^\]]*\]', '', text)
    text = re.sub(r'\*\*\*+', '', text)
    text = re.sub(r'`+', '', text)
    text = text.strip()
    return text

def format_code(text):
    text = re.sub(r'```+\s*([^`]+?)\s*```+', r'`\1`', text)
    text = re.sub(r'`+\s*([^`]+?)\s*`+', r'`\1`', text)
    text = re.sub(r'\*\*([^\*]+)\*\*`', r'**\1**', text)
    return text

def trancfer_descriprion(bitrix_task):
    task_id = bitrix_task.get('id', '')
    task_description = bitrix_task.get('description', '')
    # Add extra newlines between sections
    task_description = re.sub(r'\n([А-Я])', r'\n\n\1', task_description)
    
    code_blocks = {}
    def save_code_block(match):
        placeholder = f'__CODE_BLOCK_{len(code_blocks)}__'
        code_blocks[placeholder] = match.group(1).strip()
        return placeholder
    task_description = re.sub(r'\[CODE\](.*?)\[/CODE\]', save_code_block, task_description, flags=re.DOTALL)

    def format_size(match):
        size = match.group(1)
        text = preserve_bold(match.group(2))
        # Remove nested SIZE tags
        text = re.sub(r'\[SIZE=[^\]]+\](.*?)\[/SIZE\]', r'\1', text)
        # Just return the text without any formatting
        return text
    task_description = re.sub(r'\[SIZE=([^\]]+)\](.*?)\[/SIZE\]', format_size, task_description, flags=re.DOTALL)

    def format_color(match):
        color = match.group(1).lower()
        text = preserve_bold(match.group(2))
        if color == '#00aeef':
            return text
        elif color == '#9e005c':
            return f'`{text}`'
        elif color == '#ee1d24':
            if text.strip() == '*':
                return '*'
            else:
                base_text = text.replace('*', '')
                return f'{base_text}*'
        elif color == '#ed008c':
            return f'*{text}*'
        return text
    task_description = re.sub(r'\[COLOR=([^\]]+)\](.*?)\[/COLOR\]', format_color, task_description, flags=re.DOTALL)

    def format_font(match):
        font = match.group(1).lower()
        text = preserve_bold(match.group(2))
        if font == 'monospace':
            return f'`{text}`'
        return text
    task_description = re.sub(r'\[FONT=([^\]]+)\](.*?)\[/FONT\]', format_font, task_description, flags=re.DOTALL)

    def format_list(match):
        content = match.group(1).strip()
        items = []
        for line in content.split('[*]'):
            if line.strip():
                param_match = re.match(r'^\s*([^-]+?)\s*-\s*(.+)$', line)
                if param_match:
                    name, desc = param_match.groups()
                    name = re.sub(r'\s+', ' ', name.strip())
                    desc = desc.strip()
                    
                    if '**' in name or '*' in name:
                        base_name = name.replace('**', '').replace('*', '')
                        name = f'{base_name}*'
                    items.append(f'{name:<30} - {desc}')
                else:
                    line = line.strip()
                    if '=' in line:
                        parts = line.split('=')
                        if len(parts) == 2:
                            param = parts[0].strip()
                            value = parts[1].strip()
                            if '*' in param:
                                base_param = param.replace('*', '')
                                param = f'{base_param}*'
                            line = f'{param:<30} = {value}'
                    items.append(line)
        return '\n\n' + '\n'.join(items) + '\n\n'
    task_description = re.sub(r'\[LIST\](.*?)\[/LIST\]', format_list, task_description, flags=re.DOTALL)

    # Обработка ссылок
    task_description = re.sub(r'\[URL=([^\]]+)\](.*?)\[/URL\]', lambda m: f'[{preserve_bold(m.group(2))}]({m.group(1)})', task_description)
    task_description = re.sub(r'\[URL\](.*?)\[/URL\]', lambda m: f'[{m.group(1)}]({m.group(1)})', task_description)

    for placeholder, code in code_blocks.items():
        if '\n' in code:
            task_description = task_description.replace(placeholder, f'```\n{code}\n```')
        else:
            task_description = task_description.replace(placeholder, f'`{code}`')

    task_description = re.sub(r'\[/?[A-Z]+\]', '', task_description)

    task_description = re.sub(r'\n{3,}', '\n\n', task_description)
    task_description = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)\]\(\2\)', r'[\1](\2)', task_description)
    task_description = format_code(task_description)
    task_description = re.sub(r'\*\*\*+', '**', task_description)
    task_description = re.sub(r'\n\s*\n\s*\n+', '\n\n', task_description)
    
    return task_description.strip()
