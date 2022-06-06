from django.shortcuts import render, get_object_or_404
from .models import *
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView
from .utils import cookie_cart, cart_data, guest_order
import json
import datetime


class ProductDetail(DetailView):
    model = Product

    def get_context_data(self, *args, **kwargs):
        data = cart_data(self.request)
        cart_items = data['cart_items']
        order = data['order']
        items = data['items']

        return super().get_context_data(
            cart_items=cart_items,)


class ProductListView(ListView):
    model = Product
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        queryset = queryset.filter(category__slug=self.kwargs['slug'])   

        data = cart_data(self.request)
        cart_items = data['cart_items']
        order = data['order']
        items = data['items']

        return super().get_context_data(
            object_list=queryset,
            cart_items=cart_items,)


class Home(ListView):
    model = Category
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list

        data = cart_data(self.request)
        cart_items = data['cart_items']
        order = data['order']
        items = data['items'] 

        return super().get_context_data(
            object_list=queryset,
            cart_items=cart_items,
            )


def cart(request):
    data = cart_data(request)
    cart_items = data['cart_items']
    order = data['order']
    items = data['items'] 

    context = {'items': items, 'order': order, 'cart_items': cart_items}
    return render(request, "shop/cart.html", context)


def checkout(request):
    data = cart_data(request)
    cart_items = data['cart_items']
    order = data['order']
    items = data['items'] 

    context = {'items': items, 'order': order, 'cart_items': cart_items}
    return render(request, "shop/checkout.html", context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']
    print('action:', action)
    print('product:', product_id)

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity = (order_item.quantity + 1)
    elif action == 'remove':
        order_item.quantity = (order_item.quantity - 1)

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse('Item was added', safe=False)


def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)     

    else:
        customer, order = guest_order(request, data)
        
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            country=data['shipping']['country']
            )

    return JsonResponse('Payment complete', safe=False) #
