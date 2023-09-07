from django.contrib import admin

# Register your models here.
from .models import Restriction
from .models.category import Category
from .models.product import Product
from .models.shop_product import ShopProduct
from .models.product_state import ProductState
from .models.user_calculation import UserCalculations
from .models.products_basket import ProductsBasket
from .models.security_settings import SecuritySettings, SecurityQuestions
# adT%6i8^De

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ShopProduct)
admin.site.register(ProductState)
admin.site.register(Restriction)
admin.site.register(UserCalculations)
admin.site.register(ProductsBasket)
admin.site.register(SecuritySettings)
admin.site.register(SecurityQuestions)