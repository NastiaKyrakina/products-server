# Serializers define the API representation.
from rest_framework import serializers

from products.models import Category, ShopProduct, Product, ProductState, Restriction, UserCalculations, ProductsBasket
from products.models.diet import Diet


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category']


class ProductStateSerializer(serializers.ModelSerializer):
    energy = serializers.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        model = ProductState
        fields = ['dish_name', 'state', 'energy', 'carbohydrates', 'proteins', 'fats']


class ShopProductSerializer(serializers.HyperlinkedModelSerializer):
    product = ProductSerializer(read_only=True)
    states = ProductStateSerializer(many=True, read_only=True)

    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    class Meta:
        model = ShopProduct
        fields = ['id', 'product', 'name', 'price', 'amount', 'unit', 'states']
        extra_kwargs = {
            'amount': {'max_digits': 6, 'decimal_places': 2}
        }


class RestrictionsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Restriction
        fields = ['id', 'product', 'comparator', 'amount', 'unit']

    def create(self, validated_data):
        print(validated_data)
        product_data = validated_data.pop('product')
        restriction = Restriction.objects.create(product=product_data, **validated_data)
        return restriction


class CategoryProductSerializer(serializers.HyperlinkedModelSerializer):
    products_set = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'products_set']


class UserCalculationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCalculations
        fields = ['id', 'height', 'weight', 'years', 'sex', 'activity_level']


class ProductsBasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsBasket
        fields = ['id', 'name', 'creation_date', 'period', 'max_sum', 'products']


class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = [
            'id',
            'name',
            'description',
            'carbMin',
            'carbMax',
            'protMin',
            'protMax',
            'fatsMin',
            'fatsMax'
        ]