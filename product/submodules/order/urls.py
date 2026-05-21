from django.urls import path

from .views import (
    CreateOrderView,
    UserOrderListView,
    OrderDetailView,
    CancelOrderView
)

urlpatterns = [

    path(
        'create/',
        CreateOrderView.as_view(),
        name='create-order'
    ),

    path(
        '',
        UserOrderListView.as_view(),
        name='user-orders'
    ),

    path(
        '<int:id>/',
        OrderDetailView.as_view(),
        name='order-detail'
    ),

    path(
        '<int:id>/cancel/',
        CancelOrderView.as_view(),
        name='cancel-order'
    ),
]