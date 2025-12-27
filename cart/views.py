from django.shortcuts import render

def cart_view(request):
    return render(request, 'cart/cart.html')

def add_to_cart_view(request, id):
    return render(request, 'cart/add.html', {'product_id': id})

def remove_from_cart_view(request, id):
    return render(request, 'cart/remove.html', {'item_id': id})