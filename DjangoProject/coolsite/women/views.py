from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from requests import delete

from women.forms import *
from women.models import *
from .utils import *



# def index(request):
#     posts = Women.objects.all()
#     cont = {
#         'title': 'Home page',
#         'menu': menu,
#         'post': posts,
#         'cat_selected': 0,
#     }
#     return render(request, 'women/index.html', context=cont)

class WomenHome(DataMixin,ListView):
    model = Women
    template_name = 'women/index.html'
    context_object_name = "posts"


    def get_context_data(self, *, object_list=None, **kwargs):
        # context = super(WomenHome, self).get_context_data()
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Home Page")
        context = dict(list(context.items()) + list(c_def.items()))
        return context

    def get_queryset(self):
        return Women.objects.filter(is_published=True).select_related('cat')


def about(request):
    contact_list = Women.objects.all()
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'women/about.html', {'page_obj': page_obj, 'title': "About site", 'menu': menu})

# def addpage(request):
#     if request.method == 'POST':
#         form = AddPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             # print(form.cleaned_data)
#             form.save()
#             return redirect("home")
#     else:
#         form = AddPostForm()
#
#     return render(request, 'women/addpage.html', {'form': form, 'menu': menu, 'title': "Add article"})

class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'women/addpage.html'
    success_url = reverse_lazy('home')
    login_url = '/admin/'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Add Article')
        return dict(list(context.items()) + list(c_def.items()))


# def contact(request):
#     return HttpResponse("Feedback")

class ContactFormView(DataMixin, FormView):
    form_class = ContactForm
    template_name = 'women/contact.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Feedback")
        return context | c_def

    def form_valid(self, form):
        print(form.cleaned_data)
        return redirect('home')

# def login(request):
#     return HttpResponse("<h1>Authentication</h1>")

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>page not found</h1>")

# def show_post(request, post_slug):
#     post = get_object_or_404(Women, slug=post_slug)
#
#     context = {
#         'post': post,
#         'menu': menu,
#         'title': post.title,
#         'cat_selected': post.cat_id,
#     }
#
#     return render(request, 'women/post.html', context=context)

class ShowPost(DataMixin,DetailView):
    model = Women
    template_name = 'women/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=context["posts"])
        return dict(list(context.items()) + list(c_def.items()))



class WomenCategory(DataMixin,ListView):
    model = Women
    template_name = "women/index.html"
    context_object_name = "posts"
    allow_empty = False

    def get_queryset(self):
        return Women.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Category---' + str(c.pk),
        cat_selected=c.pk)
        return context | c_def

# def show_category(request, cat_id):
#     posts = Women.objects.filter(cat_id=cat_id)
#     if len(posts) == 0:
#         raise Http404
#     context = {
#         "posts": posts,
#         "menu": menu,
#         "title": "Show  in categories",
#         "cat_selected": cat_id,
#     }
#     return render(request, "women/index.html", context=context)

class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'women/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Registration")
        return context | c_def

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class LoginUser(DataMixin, LoginView):
    form_class = AuthenticationForm
    template_name = 'women/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Authorisation')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')

def logout_user(request):
    if User.is_authenticated:
        logout(request)
    return redirect('login')



def del_article(id):
    art = Women.objects.filter(pk=id)
    delete(art)
    return redirect('addpage.html')



