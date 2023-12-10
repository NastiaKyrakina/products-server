"""productsServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from products import views
from products.views import CategoriesListApiView, ShopProductsListApiView, ProductCalcApiView, RestrictionListApiView, \
    UserCalculationsApiView, ProductsListApiView, ProductPricesParserApiView, DietsListApiView, ProductsBasketApiView

urlpatterns = [
    path('', views.index, name='index'),
    path('categories', CategoriesListApiView.as_view()),
    path('optimization', ProductCalcApiView.as_view()),
    path('product-backet/<int:id>', ProductsBasketApiView.as_view()),
    path('shop-products', ShopProductsListApiView.as_view()),
    path('products', ProductsListApiView.as_view()),
    path('restrictions', RestrictionListApiView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user', UserCalculationsApiView.as_view()),
    path('prices', ProductPricesParserApiView.as_view()),
    path('diets', DietsListApiView.as_view()),
]
