from decimal import Decimal
import uuid

from rest_framework import serializers
from django.db import transaction

from product.submodules.order.models import Order, OrderItem
from product.submodules.cart.models import Cart
from product.models import Product


# =========================================
# Order Item Serializer
# =========================================

class OrderItemSerializer(serializers.ModelSerializer):

    product_title = serializers.CharField(
        source='product.title',
        read_only=True
    )

    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_title',
            'product_image',
            'quantity',
            'price',
            'total_price',
        ]

        read_only_fields = [
            'price',
            'total_price',
        ]

    def get_product_image(self, obj):

        request = self.context.get('request')

        if obj.product.image:

            if request:
                return request.build_absolute_uri(
                    obj.product.image.url
                )

            return obj.product.image.url

        return None


# =========================================
# Order Serializer
# =========================================

class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',

            'first_name',
            'last_name',
            'email',
            'phone',

            'address',
            'city',

            'payment_method',

            'subtotal',
            'shipping_cost',
            'discount_amount',
            'total_amount',

            'ordered_at',

            'items',
        ]


# =========================================
# Create Order Item Serializer
# =========================================

class CreateOrderItemSerializer(serializers.Serializer):

    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product(self, value):

        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Product does not exist."
            )

        return value


# =========================================
# Create Order Serializer
# =========================================

class CreateOrderSerializer(serializers.ModelSerializer):

    cart_id = serializers.CharField(write_only=True, required=False)

    product_id = serializers.IntegerField(write_only=True, required=False)
    quantity = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'city',
            'payment_method',

            'cart_id',
            'product_id',
            'quantity',
        ]

    @transaction.atomic
    def create(self, validated_data):

        cart_id = validated_data.pop('cart_id', None)
        product_id = validated_data.pop('product_id', None)
        quantity = validated_data.pop('quantity', None)

        order = Order.objects.create(
            order_number=f"ORD-{uuid.uuid4().hex[:10].upper()}",
            **validated_data
        )

        subtotal = Decimal('0.00')

        # =========================================
        # CASE 1: CART CHECKOUT
        # =========================================
        if cart_id:

            cart = Cart.objects.prefetch_related('items__product').get(cart_id=cart_id)
            items = cart.items.all()

            if not items.exists():
                raise serializers.ValidationError("Cart is empty")

            for item in items:
                product = Product.objects.select_for_update().get(id=item.product.id)
                qty = item.quantity

                if product.quantity < qty:
                    raise serializers.ValidationError(f"Insufficient stock for {product.title}")

                total = product.price * qty
                subtotal += total

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=product.price,
                    total_price=total
                )

                product.quantity -= qty
                product.save()

            cart.items.all().delete()

        # =========================================
        # CASE 2: BUY NOW (NO CART)
        # =========================================
        elif product_id and quantity:

            product = Product.objects.select_for_update().get(id=product_id)

            if product.quantity < quantity:
                raise serializers.ValidationError("Insufficient stock")

            total = product.price * quantity
            subtotal += total

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
                total_price=total
            )

            product.quantity -= quantity
            product.save()

        else:
            raise serializers.ValidationError(
                "Either cart_id OR product_id + quantity is required"
            )

        # =========================================
        # FINAL TOTALS
        # =========================================
        order.subtotal = subtotal
        order.shipping_cost = Decimal('0.00')
        order.discount_amount = Decimal('0.00')
        order.total_amount = subtotal
        order.save()

        return order