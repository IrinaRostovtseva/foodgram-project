from django import template


register = template.Library()

@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def subtract(number_1, number_2):
    return int(number_1) - int(number_2)
