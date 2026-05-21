from django.urls import path, include
from product.views import (
    ProductListView, 
    ProductDetailView, 
    ProductReviewCreateView, 
    ProductCategoryListView, 
    ProductSubCategoryListView, 
    ProductSubCategoryByCategoryView, 
    ProductByCategoryView,
    ProductBySubCategoryView,
    HeroCarouselListView,
    PopularProductsView,
    LatestProductsView,
    PopularProductsByCategoryView,
    ProductHotDealListView,
    ContuctUsCreateView
    )

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('show/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('review/create/<int:pk>/', ProductReviewCreateView.as_view(), name='product-review-create'),
    path('categories/', ProductCategoryListView.as_view(), name='category-list'),
    path('subcategories/', ProductSubCategoryListView.as_view(), name='subcategory-list'),
    path('subcategories/<int:pk>/', ProductSubCategoryByCategoryView.as_view(), name='subcategory-by-category'),
    path('category/<int:pk>/products/', ProductByCategoryView.as_view(), name='packages-by-direct-category'),
    path('subcategory/<int:pk>/products/', ProductBySubCategoryView.as_view(), name='packages-by-direct-category'),
    path('hero-carousel/', HeroCarouselListView.as_view(), name='hero-carousel-list'),
    path('products/popular/', PopularProductsView.as_view(), name='popular-products'),
    path('products/latest/', LatestProductsView.as_view(), name='latest-products'),
    path('products/popular/category/<int:pk>/', PopularProductsByCategoryView.as_view(), name='popular-products-by-category'),
    path('hot-deals/', ProductHotDealListView.as_view(), name='hot-deal-products'),
    path('contact-us/', ContuctUsCreateView.as_view(), name='contact-us'),
    path('cart/', include('product.submodules.cart.urls')),
    path('order/', include('product.submodules.order.urls')),
]