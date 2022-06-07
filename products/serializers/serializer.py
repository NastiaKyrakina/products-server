# Serializers define the API representation.
from rest_framework import serializers

from products.models import Category, ShopProduct, Product, ProductState, Restriction, UserCalculations


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
        fields = ['height', 'weight', 'years', 'sex', 'activity_level']


# user = models.OneToOneField(User, on_delete=models.CASCADE)
# height = models.FloatField()
# weight = models.FloatField()
# years = models.IntegerField()
# sex = models.CharField(max_length=2, choices=SEX_CHOICES)
# activity_level = models.CharField(max_length=2, choices=ACTIVITY_CHOICES)
 # product = models.ForeignKey(Product, on_delete=models.CASCADE)
 #    name = models.CharField(max_length=350)
 #    price = models.DecimalField(max_digits=6, decimal_places=2)
 #    amount = models.DecimalField(max_digits=6, decimal_places=2)
 #    unit = models.CharField(max_length=3)
 #    states = models.ManyToManyField(ProductState)
 #    default = models.BooleanField(default=True)