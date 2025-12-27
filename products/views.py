from django.shortcuts import render

def product_list_view(request):
    return render(request, 'products/list.html')

def product_detail_view(request, id):
    return render(request, 'products/detail.html', {'product_id': id})

def category_view(request, slug):
    return render(request, 'products/category.html', {'category_slug': slug})