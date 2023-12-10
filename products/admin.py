from django.contrib import admin

# Register your models here.
from .models import Restriction
from .models.category import Category
from .models.diet import Diet
from .models.diet_catefory_restriction import DietCategoryRestriction
from .models.diet_product_restriction import DietProductRestriction
from .models.product import Product
from .models.shop_product import ShopProduct
from .models.product_state import ProductState
from .models.user_calculation import UserCalculations
from .models.products_basket import ProductsBasket
# adT%6i8^De

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ShopProduct)
admin.site.register(ProductState)
admin.site.register(Restriction)
admin.site.register(UserCalculations)
admin.site.register(ProductsBasket)

admin.site.register(Diet)
admin.site.register(DietCategoryRestriction)
admin.site.register(DietProductRestriction)