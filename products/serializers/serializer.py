# Serializers define the API representation.
from rest_framework import serializers

from products.models import Category, ShopProduct, Product, ProductState


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'category']


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


class CategoryProductSerializer(serializers.HyperlinkedModelSerializer):
    products_set = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'products_set']

 # product = models.ForeignKey(Product, on_delete=models.CASCADE)
 #    name = models.CharField(max_length=350)
 #    price = models.DecimalField(max_digits=6, decimal_places=2)
 #    amount = models.DecimalField(max_digits=6, decimal_places=2)
 #    unit = models.CharField(max_length=3)
 #    states = models.ManyToManyField(ProductState)
 #    default = models.BooleanField(default=True)