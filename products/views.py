import json
import logging

from django.contrib.auth.models import User

# Create your views here.
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.helpers import product_prices_parcer
from products.helpers.json_to_exel import write_to_file
from products.models import Category, ShopProduct, Restriction, Product, UserCalculations, ProductsBasket
from products.models.diet import Diet
from products.models.diet_catefory_restriction import DietCategoryRestriction
from products.models.diet_product_restriction import DietProductRestriction
from products.serializers.serializer import ShopProductSerializer, CategoryProductSerializer, \
    RestrictionsSerializer, UserCalculationsSerializer, ProductsBasketSerializer, ProductSerializer, DietSerializer
from products.service import optimize_products_bucket
from datetime import datetime
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger('django')

default_energy_restrictions = dict({
        'carbohydrates': (0.55, 0.6),
        'proteins': (0.15, 0.20),
        'fats': (0.2, 0.25),
     })


class ProductCalcApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(operation_description="Get list of products baskets for user", responses={200: ProductsBasketSerializer(many=True)})
    # 1. List all
    def get(self, request, *args, **kwargs):
        baskets = ProductsBasket.objects.filter(user_id=request.user.pk)
        serializer = ProductsBasketSerializer(baskets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Optimize products buckets for user",
                         responses={200: ProductsBasketSerializer()})
    def post(self, request, *args, **kwargs):
        print(request.data)
        products = request.data.get('products')
        diet_id = request.data.get('dietId')
        custom_energy_restrictions = request.data.get('energyRestrictions')
        energy_per_day = request.data.get('energyAmount')
        max_sum = request.data.get('maxSum')
        term = int(request.data.get('term'))
        shop_products = products if len(products) else ShopProduct.objects.prefetch_related('states').all()
        diet = Diet.objects.get(id = diet_id)
        diet_restrictions = DietProductRestriction.objects.prefetch_related('restriction').filter(diet_id=diet_id).all();
        print(diet_restrictions)
        restrictions = Restriction.objects.prefetch_related('product').filter(default=True).all()
        category_restrictions = DietCategoryRestriction.objects.filter(diet_id=diet_id).all()
        products_list = prepare_products_for_calc(shop_products, len(products) == 0, diet_restrictions, category_restrictions)
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


def prepare_products_for_calc(shop_products, from_db, diet_restrictions, category_restrictions):

    products_list = list()
    print(category_restrictions)
    for product in shop_products:
        restricted_category = [x for x in category_restrictions if x.category_id == product.product.category.id]
        print('restricted_category:', restricted_category)
        if len(restricted_category) > 0:
            continue
        states = product.states.all() if from_db else product.states
        parsed_restrictions = list()
        product_restrictions = [x for x in diet_restrictions if is_product_restriction(product.product.id, x)]
        for diet_restriction in product_restrictions:
            amount = amount_to_gr(diet_restriction.restriction.unit, float(str(diet_restriction.restriction.amount)))
            parsed_restrictions.append({
                "comparator": diet_restriction.restriction.comparator,
                "amount": amount,
                'unit': diet_restriction.restriction.unit,
            })
        for state in states:
            amount = amount_to_gr(product.unit, float(str(product.amount)))
            excludeProduct = False
            for restriction in parsed_restrictions:
                if restriction['amount'] == 0 and (restriction['comparator'] == 'LT' or restriction['comparator'] == 'GT'):
                    excludeProduct = True
            if  not excludeProduct:
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


def is_product_restriction(product_id, diet_restrictions):
    return product_id == diet_restrictions.restriction.product_id

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
        downloadAsFile = request.query_params.get('downloadAsFile')
        print(downloadAsFile)
        basket = ProductsBasket.objects.get(id=kwargs['id'])
        serializer = ProductsBasketSerializer(basket)
        if downloadAsFile:
            file_contend = write_to_file(json.loads(serializer.data.get('products')))
            filename = "django_simple.xlsx"
            response = HttpResponse(
                file_contend,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = "attachment; filename=%s" % filename
            return response

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
    @swagger_auto_schema(operation_description="List of user restrictions",
                         responses={200: RestrictionsSerializer()})
    def get(self, request, *args, **kwargs):
        print(request.user.pk)
        print(request.user.is_authenticated)
        restrictions = Restriction.objects.prefetch_related('product').all()
        serializer = RestrictionsSerializer(restrictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Add user restriction", request_body=RestrictionsSerializer(),
                         responses={200: RestrictionsSerializer()})
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
    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        shopProducts = ShopProduct.objects.prefetch_related('product', 'product__category', 'states').all()
        serializer = ShopProductSerializer(shopProducts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        product = Product.objects.get(pk=request.data.get('product'))
        data = request.data.copy()
        data['product'] = product
        shopProductSerializer = RestrictionsSerializer(data=data)
        if shopProductSerializer.is_valid():
            ShopProduct.objects.create(**data)
            return Response(shopProductSerializer.data, status=status.HTTP_201_CREATED)
        return Response(shopProductSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        shopProduct = ShopProduct.objects.get(pk=request.data.get('id'))
        data = request.data.copy()
        shopProductSerializer = RestrictionsSerializer(data=data)
        if shopProductSerializer.is_valid():
            shopProduct.update(**data)
            return Response(shopProductSerializer.data, status=status.HTTP_201_CREATED)
        return Response(shopProductSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductsListApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        products = Product.objects.prefetch_related('category').all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        productSerializer = ProductSerializer(data=data)
        if productSerializer.is_valid():
            Product.objects.create(**data)
            return Response(productSerializer.data, status=status.HTTP_201_CREATED)
        return Response(productSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

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