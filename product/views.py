from django.db.models import F
from django.db.models import Q
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from product.models import Product, Category, SubCategory, HeroCarousel
from product.serializers import (
    ContactUsSerializer, 
    ProductListSerializer, 
    ProductSerializer, 
    ReviewSerializer, 
    ProductCategorySerializer, 
    ProductSubCategorySerializer, 
    HeroCarouselSerializer)
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from backend.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny

from rest_framework.filters import OrderingFilter, SearchFilter


@extend_schema(
    tags=["Products"],
    summary="List All Products",
    description="""
Returns a list of all available products.  
This endpoint is publicly accessible and does not require authentication.
""",
    responses={
        200: ProductListSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            name="Product List Example",
            description="Example response showing multiple products",
            value=[
                {
                    "id": 1,
                    "title": "iPhone 15",
                    "price": "1200.00",
                    "quantity": 10,
                    "created_at": "2026-04-09T10:00:00Z"
                },
                {
                    "id": 2,
                    "title": "Samsung Galaxy S24",
                    "price": "1100.00",
                    "quantity": 15,
                    "created_at": "2026-04-08T08:30:00Z"
                }
            ],
            response_only=True
        )
    ]
)
class ProductListView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Product.objects.prefetch_related('categories', 'sub_categories','Product_colors')
    serializer_class = ProductListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    search_fields = ['title']
    ordering_fields = ['price', 'quantity', 'created_at']
    filterset_fields = {
    'price': ['exact', 'gte', 'lte'],
    'quantity': ['exact', 'gte', 'lte'],
    'categories': ['exact'],
    'hot_deal': ['exact'],
}

@extend_schema(
    tags=["Products"],
    summary="Get Product Details",
    description="""
Retrieve detailed information about a specific product using its ID.
""",
    responses={
        200: ProductSerializer,
        404: OpenApiExample(
            name="Product Not Found",
            value={"error": "Product not found"},
            response_only=True,
            status_codes=["404"]
        )
    },
    examples=[
        OpenApiExample(
            name="Product Detail Example",
            description="Example response for a single product",
            value={
                "id": 1,
                "title": "iPhone 15",
                "description": "Latest Apple smartphone",
                "price": "1200.00",
                "quantity": 10,
                "category": 1,
                "subcategory": 2,
                "created_at": "2026-04-09T10:00:00Z"
            },
            response_only=True
        )
    ]
)
class ProductDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request, pk):
        try:
            product = Product.objects.prefetch_related('categories', 'sub_categories', 'images', 'Product_colors','product_faqs', 'product_reviews').get(pk=pk)
            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["Reviews"],
    summary="Create Product Review",
    description="Create a review for a specific product using product ID.",

    request= ReviewSerializer,

    responses=ReviewSerializer
)
class ProductReviewCreateView(APIView):
    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(product=product)
                product.update_average_rating()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        

@extend_schema(
    tags=["Categories"], 
    summary="List all categories", 
    description="Get a list of all product categories with their subcategories and products",
    responses={200: ProductCategorySerializer(many=True)})
class ProductCategoryListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request):
        
        """
        Get a list of all product categories with their subcategories and products.

        If the data is cached, return the cached data. Otherwise, retrieve the data
        from the database, serialize it, cache the result for 10 minutes, and
        return the serialized data.

        Returns:
            Response: A JSON response containing a list of product categories with
                their subcategories and products.
        """
        cache_key = 'product_categories_list'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
            
        try:
            categories = Category.objects.prefetch_related(
                'subcategories',
                'products_category'
            ).all()
            serializer = ProductCategorySerializer(categories, many=True)
            response_data = serializer.data
            
            # Cache for 10 minutes
            cache.set(cache_key, response_data, 600)
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["Subcategories"], 
    summary="List all subcategories", 
    description="Get a list of all product subcategories",
    responses={200: ProductSubCategorySerializer(many=True)})
class ProductSubCategoryListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request):
        
        """
        Get a list of all product subcategories.

        Returns:
            Response: A JSON response containing a list of product subcategories.
        """
        try:
            subcategories = SubCategory.objects.all()
            serializer = ProductSubCategorySerializer(subcategories, many=True,context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Subcategories not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=["Subcategories"],
    summary="List subcategories by category",
    description="Retrieve all subcategories for a specific category using its ID (primary key).",
    responses={
        200: ProductSubCategorySerializer(many=True),
        
    }
)
class ProductSubCategoryByCategoryView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request, pk):
        
        """
        Get subcategories for a specific category.

        Args:
            request (Request): The incoming request.
            pk (int): The primary key of the category.

        Returns:
            Response: A JSON response containing a list of subcategories.
        """
        try:
            category = Category.objects.get(pk=pk)
            subcategories = category.subcategories.all()
            serializer = ProductSubCategorySerializer(subcategories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Subcategories not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=["Products"],
    summary="Get products by category (including subcategories)",
    description="Retrieve all products assigned to a category and its subcategories.",
    responses={200: ProductListSerializer(many=True)}
)
class ProductByCategoryView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request, pk):
        
        """
        Get products assigned to a specific category, including tours from its subcategories.

        Args:
            request (Request): The incoming request.
            pk (int): The primary key of the category.

        Returns:
            Response: A JSON response containing a list of products.
        """
        
        
        try:            
            # Get products from:
            # 1. Direct products in main category
            # 2. Products in subcategories
            products = Product.objects.prefetch_related(
                'Product_colors',
                'sub_categories',
                'categories'
            ).filter(
                Q(categories__id=pk) |  # Direct category products
                Q(categories__subcategories__category_id=pk)  # Subcategory products
            ).distinct()
            
            serializer = ProductListSerializer(products, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@extend_schema(
    tags=["Products"],
    summary="Get products by sub-category ",
    description="Retrieve all products assigned to a subcategory",
    responses={200: ProductListSerializer(many=True)}
)
class ProductBySubCategoryView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request, pk):
        
        """
        Get products assigned to a specific category, including tours from its subcategories.

        Args:
            request (Request): The incoming request.
            pk (int): The primary key of the category.

        Returns:
            Response: A JSON response containing a list of products.
        """
        
        
        try:            
            # subcategory = SubCategory.objects.get(pk=pk)
            
            products = Product.objects.select_related().prefetch_related(
                'Product_colors',
                'sub_categories',
                'categories'
            ).filter(
                sub_categories__id=pk  # Subcategory products
            ).distinct()
            
            serializer = ProductListSerializer(products, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SubCategory.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
@extend_schema(
    tags=["Hero Carousel"],
    summary="List Hero Carousel items",
    description="Retrieve a list of all hero carousel items for the homepage display.",
    responses={200: HeroCarouselSerializer(many=True)}
)
class HeroCarouselListView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = HeroCarousel.objects.all()
    serializer_class = HeroCarouselSerializer
    pagination_class = None  # Disable pagination for this view 


@extend_schema(
    tags=["Products"],
    summary="Get popular products",
    description="Retrieve top 10 products sorted by highest average rating.",
    responses={200: ProductListSerializer(many=True)}
)
class PopularProductsView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Product.objects.prefetch_related('categories', 'sub_categories','Product_colors').order_by(F('average_rating').desc(nulls_last=True))[:10]
    serializer_class = ProductListSerializer
    pagination_class = None  # Disable pagination for this view


@extend_schema(
    tags=["Products"],
    summary="Get latest products",
    description="Retrieve the 10 most recently created products.",
    responses={200: ProductListSerializer(many=True)}
)
class LatestProductsView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Product.objects.prefetch_related('categories', 'sub_categories','Product_colors').order_by('-created_at')[:10]
    serializer_class = ProductListSerializer
    pagination_class = None  # Disable pagination for this view

@extend_schema(
    tags=["Products"],
    summary="Get popular products by category",
    description="Retrieve top 10 highest-rated products for a specific category.",
    responses={
        200: ProductListSerializer(many=True),
        404: {"type": "object", "properties": {"error": {"type": "string"}}}
    }
)
class PopularProductsByCategoryView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
            products = Product.objects.prefetch_related('categories', 'sub_categories','Product_colors').filter(categories=category).order_by(F('average_rating').desc(nulls_last=True))[:10]
            serializer = ProductListSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@extend_schema(
    tags=["Products"],
    summary="Get hot deal products",
    description="Retrieve all products marked as hot deals.",
    responses={200: ProductListSerializer(many=True)}
)
class ProductHotDealListView(generics.ListAPIView):
    queryset = Product.objects.prefetch_related('categories', 'sub_categories', 'Product_colors').filter(hot_deal=True)
    serializer_class = ProductListSerializer
    pagination_class = None  # Disable pagination for this view


@extend_schema(
    tags=["Contact Us"],
    summary="Contact us API",
    description="Send a message via contact form",
    request=ContactUsSerializer,
    responses={
        201: OpenApiResponse(response=ContactUsSerializer, description="Message created")
    }
)
class ContuctUsCreateView(generics.CreateAPIView):
    serializer_class = ContactUsSerializer