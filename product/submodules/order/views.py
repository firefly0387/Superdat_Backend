from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from product.submodules.order.models import Order
from product.submodules.order.serializers import (
    OrderSerializer,
    CreateOrderSerializer
)


# =========================================
# Create Order
# =========================================

@extend_schema(
    tags=["Orders"],
    summary="Create order",
    description="Create a new order with items and billing details.",
    request=CreateOrderSerializer,
    responses={201: OrderSerializer}
)
class CreateOrderView(generics.CreateAPIView):

    serializer_class = CreateOrderSerializer

    def get_serializer_context(self):

        return {
            'request': self.request,
        }

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        response_serializer = OrderSerializer(
            order,
            context=self.get_serializer_context()
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


# =========================================
# User Orders List
# =========================================

@extend_schema(
    tags=["Orders"],
    summary="Get user orders",
    description="Retrieve all orders of authenticated user.",
    responses={200: OrderSerializer(many=True)}
)
class UserOrderListView(generics.ListAPIView):

    serializer_class = OrderSerializer

    def get_queryset(self):

        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related(
                'items',
                'items__product'
            )
            .order_by('-ordered_at')
        )


# =========================================
# Order Detail
# =========================================

@extend_schema(
    tags=["Orders"],
    summary="Get order details",
    description="Retrieve specific order details.",
    responses={200: OrderSerializer}
)
class OrderDetailView(generics.RetrieveAPIView):

    serializer_class = OrderSerializer
    lookup_field = 'id'

    def get_queryset(self):

        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related(
                'items',
                'items__product'
            )
        )


# =========================================
# Cancel Order
# =========================================

@extend_schema(
    tags=["Orders"],
    summary="Cancel order",
    description="Cancel a pending order.",
    responses={200: OrderSerializer}
)
class CancelOrderView(APIView):


    def post(self, request, id):

        order = get_object_or_404(
            Order,
            id=id,
            user=request.user
        )

        # Prevent cancelling completed orders
        if order.status != 'pending':

            return Response(
                {
                    'error': (
                        'Only pending orders can be cancelled.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'cancelled'
        order.save(update_fields=['status'])

        serializer = OrderSerializer(
            order,
            context={'request': request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )