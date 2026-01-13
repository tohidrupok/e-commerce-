from django import template

register = template.Library()

@register.filter
def bd_format(value):
    try:
        value = float(value)
    except Exception:
        return value

    integer, decimal = f"{value:.2f}".split(".")
    integer = integer[::-1]

    parts = [integer[:3]]
    integer = integer[3:]

    while integer:
        parts.append(integer[:2])
        integer = integer[2:]

    formatted = ",".join(parts)[::-1]
    return f"{formatted}.{decimal}"
