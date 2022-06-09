from django.contrib import admin

# Register your models here.
from .models import Restriction
from .models.category import Category
from .models.product import Product
from .models.shop_product import ShopProduct
from .models.product_state import ProductState
from .models.user_calculation import UserCalculations

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ShopProduct)
admin.site.register(ProductState)
admin.site.register(Restriction)
admin.site.register(UserCalculations)
