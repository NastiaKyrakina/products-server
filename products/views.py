import json
from unicodedata import decimal

from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ValidationError
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, status
from rest_framework.decorators import authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.backends import TokenBackend

from products.models import Category, ShopProduct, Restriction, Product, UserCalculations, ProductsBasket
from products.serializers.serializer import CategorySerializer, ShopProductSerializer, CategoryProductSerializer, \
    RestrictionsSerializer, UserCalculationsSerializer, ProductsBasketSerializer
from products.service import optimize_products_bucket


class ProductCalcApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        baskets = ProductsBasket.objects.all()
        serializer = ProductsBasketSerializer(baskets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        print(request.data)
        # serializer = SnippetSerializer(data=request.data)
        products = request.data.get('products')
        energy_per_day = request.data.get('energyAmount')
        max_sum = request.data.get('maxSum')
        term = request.data.get('term')
        shop_products = products if len(products) else ShopProduct.objects.prefetch_related('states').all()
        products_list = prepare_products_for_calc(shop_products, len(products) == 0)
        sol = optimize_products_bucket(products_list, [], max_sum, energy_per_day)
        if request.user.is_authenticated:
            sol_json = json.dumps(sol, default=lambda o: o.__dict__, ensure_ascii=False, sort_keys=True, indent=4)
            basket = dict()
            basket['name'] = 'test basket'
            basket['period'] = 1
            basket['max_sum'] = max_sum
            basket['user'] = request.user
            basket['products'] = sol_json
            ProductsBasket.objects.create(**basket)
        return Response({'optimization': sol, 'products': products_list}, status=status.HTTP_200_OK)


def prepare_products_for_calc(shop_products, from_db):
    products_list = list()
    for product in shop_products:
        states = product.states.all() if from_db else product.states
        for state in states:
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
    return products_list


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


class RestrictionListApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]
    # 1. List all

    def get(self, request, *args, **kwargs):
        print(request.user.pk)
        print(request.user.is_authenticated)
        restrictions = Restriction.objects.prefetch_related('product').all()
        serializer = RestrictionsSerializer(restrictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        product = Product.objects.get(pk=request.data.get('product'))
        data = request.data.copy()
        data['product'] = product
        restrictionsSerializer = RestrictionsSerializer(data=data)
        if restrictionsSerializer.is_valid():
            Restriction.objects.create(**data)
            return Response(restrictionsSerializer.data, status=status.HTTP_201_CREATED)
        return Response(restrictionsSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        return amount * 1000
    if unit == 'л':
        return amount * 1000
    if unit == 'мл':
        return amount
    if unit == 'мг':
        return amount * 0.001
    if unit == 'шт':
        return amount
    return amount


class UserCalculationsApiView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print(request.user.pk)
        print(request.user.is_authenticated)
        userCalculations = User.objects.get(id=request.user.pk).usercalculations
        serializer = UserCalculationsSerializer(userCalculations)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        data['user'] = user
        user_calculations = UserCalculations.objects.create(**data)
        serializer = UserCalculationsSerializer(user_calculations)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")