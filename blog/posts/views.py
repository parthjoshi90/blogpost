from django.contrib import messages
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Post
from django.utils import timezone
from .forms import PostForm
from .models import Post
from django.db.models import Q
from django.contrib.auth import logout

def post_create(request):
    if request.user.is_staff or not request.user.is_superuser:
        form = PostForm(request.POST or None, request.FILES or None)
        # form = PostForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user= request.user
            instance.save()
        # mesage of success
            messages.success(request, "Successfully Created")
            return HttpResponseRedirect(instance.get_absolute_url())
            
        context = {
            "form": form,
        }
        return render(request, "post_form.html", context)
    else:
        raise Http404

def post_detail(request, slug=None):  
        if request.user.is_staff or not request.user.is_superuser:
            instance = get_object_or_404(Post, slug=slug)
            context = {
                "title": instance.title,
                "instance": instance,
                "image": instance.image,
            }
            return render(request, "post_detail.html", context)
        else:
            raise Http404()
    

def post_list(request):
    queryset_list= Post.objects.active()   #order_by("-timestamp","-update")
    if request.user.is_staff or request.user.is_superuser:
        queryset_list= Post.objects.all()

    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
                Q(title__icontains=query)|
                Q(content__icontains=query)|
                Q(user__first_name__icontains=query)|
                Q(user__last_name__icontains=query)
                ).distinct()
    paginator = Paginator(queryset_list, 4) 
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:

        queryset = paginator.page(paginator.num_pages)
    context = {
        "object_list": queryset,
        "title": "List",
        "page_request_var": page_request_var
    }
    return render(request, "post_list.html", context)

def post_update(request, slug=None):
    if request.user.is_staff or not request.user.is_superuser:
        instance = get_object_or_404(Post, slug=slug)
        form = PostForm(request.POST or None, request.FILES or None, instance=instance)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, "Successfully Updated")
            return HttpResponseRedirect(instance.get_absolute_url())
        
        context = {
            "title": instance.title,
            "instance": instance,
            "form": form,
        }
        return render(request, "post_form.html", context)
    else:
        raise Http404()


def post_delete(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        instance = get_object_or_404(Post, slug=slug)
        instance.delete()
        messages.success(request, "Successfully Deleted")
        return redirect("post:list")
    else:
        raise Http404()



def user_logout(request):
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect('/posts/')

