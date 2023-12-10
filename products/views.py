import json
import logging
from random import random, randrange
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

from products import product_prices_parcer
from products.models import Category, ShopProduct, Restriction, Product, UserCalculations, ProductsBasket
from products.models.diet import Diet
from products.serializers.serializer import CategorySerializer, ShopProductSerializer, CategoryProductSerializer, \
    RestrictionsSerializer, UserCalculationsSerializer, ProductsBasketSerializer, ProductSerializer, DietSerializer
from products.service import optimize_products_bucket
from datetime import datetime


logger = logging.getLogger('django')

default_energy_restrictions = dict({
        'carbohydrates': (0.55, 0.6),
        'proteins': (0.15, 0.20),
        'fats': (0.2, 0.25),
     })


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
        diet_id = request.data.get('dietId')
        custom_energy_restrictions = request.data.get('energyRestrictions')
        energy_per_day = request.data.get('energyAmount')
        max_sum = request.data.get('maxSum')
        term = int(request.data.get('term'))
        shop_products = products if len(products) else ShopProduct.objects.prefetch_related('states').all()
        restrictions = Restriction.objects.prefetch_related('product').all()
        products_list = prepare_products_for_calc(shop_products, len(products) == 0, restrictions)

        energy_restrictions = custom_energy_restrictions if custom_energy_restrictions else default_energy_restrictions

        sol = optimize_products_bucket(products_list, [], max_sum, energy_per_day, energy_restrictions, term)
        if request.user.is_authenticated:
            sol_json = json.dumps(sol, default=lambda o: o.__dict__, ensure_ascii=False, sort_keys=True, indent=4)
            basket = dict()
            now = datetime.now()
            t_string = now.strftime("%d/%m/%Y %H:%M:%S")
            basket['name'] = 'Список за ' + t_string
            basket['period'] = 1
            basket['max_sum'] = max_sum
            basket['user'] = request.user
            basket['products'] = sol_json
            ProductsBasket.objects.create(**basket)
        return Response({'optimization': sol, 'products': products_list}, status=status.HTTP_200_OK)


def prepare_products_for_calc(shop_products, from_db, restrictions):

    products_list = list()
    for product in shop_products:
        states = product.states.all() if from_db else product.states
        parsed_restrictions = list()
        product_restrictions = [x for x in restrictions if is_product_restriction(product.product.id, x)]
        for restriction in product_restrictions:
            amount = amount_to_gr(restriction.unit, float(str(restriction.amount)))
            parsed_restrictions.append({
                "comparator": restriction.comparator,
                "amount": amount,
                'unit': restriction.unit,
            })
        print(parsed_restrictions)
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
                'restrictions': parsed_restrictions,
            })
    return products_list


def is_product_restriction(product_id, restriction):
    return product_id == restriction.product.id

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

class ProductsBasketApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]
    # 1. List all

    def get(self, request, *args, **kwargs):
        print(kwargs['id']);
        basket = ProductsBasket.objects.get(id=kwargs['id'])
        serializer = ProductsBasketSerializer(basket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def post(self, request, *args, **kwargs):
    #     product = Product.objects.get(pk=request.data.get('product'))
    #     data = request.data.copy()
    #     data['product'] = product
    #     restrictionsSerializer = RestrictionsSerializer(data=data)
    #     if restrictionsSerializer.is_valid():
    #         Restriction.objects.create(**data)
    #         return Response(restrictionsSerializer.data, status=status.HTTP_201_CREATED)
    #     return Response(restrictionsSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class ShopProductsListApiView(APIView):
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


class ProductsListApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        shopProducts = Product.objects.prefetch_related('category').all()
        serializer = ProductSerializer(shopProducts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DietsListApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        diets = Diet.objects.all()
        serializer = DietSerializer(diets, many=True)
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
        logger.info("Customer " + str(request.user.pk) + " request data for calculations")
        userCalculations = User.objects.get(id=request.user.pk).usercalculations
        serializer = UserCalculationsSerializer(userCalculations)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        logger.info("Customer " + str(request.user.pk) + " send data for calculations")
        user = request.user
        data = request.data.copy()
        data['user'] = user
        user_calculations = UserCalculations.objects.create(**data)
        serializer = UserCalculationsSerializer(user_calculations)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class ProductPricesParserApiView(APIView):
    def get(self, request, *args, **kwargs):
        product_prices = product_prices_parcer.parce_page()
        print(product_prices)
        for product in product_prices:
            price = product.get('average')[0].get('price').replace(',', '.')
            print('Name: ' + product.get('name'))
            print('price: ' + price)
            try:
                product_in_shop = ShopProduct.objects.filter(name=product.get('name')).update(**{'price': float(price)})
            except ShopProduct.DoesNotExist:
                print('Can`t update product price')
            print('__________________')
        return HttpResponse("Hello, world. You're at the polls index.")