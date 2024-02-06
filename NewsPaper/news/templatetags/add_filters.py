import re
from django import template

register = template.Library()

BAD_WORDS = ['', '', '']  # здесь добавим нецензурные слова, можно сделать отдельный файл.


@register.filter(name='censor')
def censor(input_str):
    if not isinstance(input_str, str):
        raise ValueError('Цензор применяется только к строке!')
    for word in BAD_WORDS:
        if word and len(word) > 0:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            input_str = pattern.sub(f'{word[0]}{"*"*(len(word)-1)}', input_str)
            # return input_str.lower().replace(word, f'{word[0]}{"*" * (len(word) - 1)}')
    return input_str
