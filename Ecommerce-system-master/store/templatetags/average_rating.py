from django import template
from store.models import Review
from django.db.models import Avg

register = template.Library()


# @register.inclusion_tag('core/menu.html')
@register.filter
def avg_rating(product):
    try:
        a = Review.objects.filter(product_id=product.id).aggregate(Avg('rating'))
        if a['rating__avg'] > 0:
            b = int(float(a['rating__avg']) * 20)
            return b
        else:
            b = 0
            return b
    except:
        b = 0
        return b


@register.filter
def review_count(product):
    p = Review.objects.filter(product_id=product.id).count()
    return p
