from django.shortcuts import render

def checkout_view(request):
    return render(request, 'orders/checkout.html')

def order_detail_view(request, id):
    return render(request, 'orders/detail.html', {'order_id': id})

def order_history_view(request):
    return render(request, 'orders/history.html')