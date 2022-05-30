from unicodedata import decimal

from django.core import serializers
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Category, ShopProduct
from products.serializers.serializer import CategorySerializer, ShopProductSerializer, CategoryProductSerializer
from products.service import optimize_products_bucket


class ProductCalcApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        shopProducts = ShopProduct.objects.prefetch_related('states').all()
        products_list = list()
        for product in shopProducts:
            for state in product.states.all():
                amount = amount_to_gr(product.unit, float(str(product.amount)))
                products_list.append({
                    'id': product.id,
                    'name': product.name,
                    'unit': product.unit,
                    'price': float(str(product.price)) / amount,
                    'amount': amount,
                    'energy': float(str(state.energy)) / 100,
                    'carbohydrates': float(str(state.carbohydrates)) / 100,
                    'proteins': float(str(state.proteins)) / 100,
                    'fats': float(str(state.fats)) / 100,
                })
        sol = optimize_products_bucket(products_list, [], max_sum=2000, kkal_per_day=2568)
        return Response({'optimization': sol, 'products': products_list}, status=status.HTTP_200_OK)


class CategoriesListApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        categories = Category.objects.prefetch_related('product_set').all()
        serializer = CategoryProductSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductsListApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        shopProducts = ShopProduct.objects.prefetch_related('product', 'product__category', 'states').all()
        serializer = ShopProductSerializer(shopProducts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def amount_to_gr(unit, amount):
    if unit == 'кг':
        return amount*1000
    if unit == 'л':
        return amount*1000
    if unit == 'мл':
        return amount
    if unit == 'мг':
        return amount*0.001
    if unit == 'шт':
        return amount
    return amount

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def get_categories(request):
    categories = Category.objects.values()
    categories_list = list(categories)
    return JsonResponse({'data': categories_list}, json_dumps_params={'ensure_ascii': False})


def get_shop_products(request):
    shop_products = ShopProduct.objects.select_related('product__category').all()
    for product in shop_products:
        print(product.states.all().values())
    shop_products_list = list(shop_products.values())
    return JsonResponse({'data': shop_products_list}, json_dumps_params={'ensure_ascii': False}, safe=False)

