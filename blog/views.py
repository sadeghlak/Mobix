from django.shortcuts import render

def blog_list_view(request):
    return render(request, 'blog/list.html')

def blog_detail_view(request, id):
    return render(request, 'blog/detail.html', {'post_id': id})