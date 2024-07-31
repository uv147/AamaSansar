from django.shortcuts import render

from ecomadmin.models import Banner, About
from recommendation.data_collection import recommend_popularity_based
from store.models import Product, Category


def frontpage(request):
    try:
        products = Product.objects.filter(status=Product.ACTIVE).order_by('?')[:16]
        categories = Category.objects.all()
        banners = Banner.objects.all().order_by('-weight')[:6]
        about = About.objects.all().first()
        popular_products = recommend_popularity_based(request)
        popular_products = popular_products.filter(status="Active")
        print(popular_products)
        return render(request, 'core/index.html', {
            'products': products,
            'popular_products': popular_products,
            'categories': categories,
            'banners': banners,
            'about': about,
        })
    except:
        pass
