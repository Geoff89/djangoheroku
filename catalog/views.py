from datetime import datetime
import datetime
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Book, Author, BookInstance
from catalog.forms import RenewBookForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
#@permission_required('catalog.can_mark_returned')
#@permission_required('catalog.can_edit')
@login_required()
def index(request):
    """View function for home page"""

    #Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    #Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    #The 'all()' is implied by degfault
    num_authors = Author.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_avaiable': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits
    }

    #Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

#signup page
def SignUp(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})            


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book    
    context_object_name = 'book_list'
    template_name = 'book_list.html'
    paginate_by = 3

#Detail article

class BookDetailView(generic.DetailView):
    model = Book
    context_object_name = 'book'
    template_name = 'book_detail.html'

class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    context_object_name = 'author_list'
    template_name = 'author_list.html'
    paginate_by = 10

class AuthorDetailview(generic.DetailView):
    model = Author
    context_object_name = 'author'
    template_name = 'author_detail.html'

class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death'] 
    initial = {'date_of_death': '11/06/2020'} 
    
class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__'
    
class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    
     
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class based view listing book on loan to current user""" 
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'   
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LibrarianListView(LoginRequiredMixin,PermissionRequiredMixin, generic.ListView):
    """Generic class based view listing book on loan to current user""" 
    model = BookInstance
    template_name = 'catalog/librarianview.html'   
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
    
    
@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    #If this is a Post request then process the form data
    if request.method == 'POST':

        #create a form instance and populate it with data from the request(binding)
        form = RenewBookForm(request.POST)

        #check if the form is valid
        if form.is_valid():
            #peocess the data in form.cleaned_data as required.(here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            #redirect to anew URl
            return HttpResponseRedirect(reverse('librarian-view'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

        context = {
            'form': form,
            'book_instance': book_instance,
        }  

        return render(request, 'catalog/book_renew_librarian.html', context)


"""
class MyView(PermissionRequiredMixin, View):
    permission_required = 'catalog.can_mark_returned'
    # Or multiple permissions
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    # Note that 'catalog.can_edit' is just an example
    # the catalog application doesn't have such permission!

Listing 10-6. Permission check in view methods with @user_passes_test and @permission_required

# Method check to see if User belongs to group called 'Barista'
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group

@user_passes_test(lambda u: Group.objects.get(name='Baristas') in u.groups.all())
def dashboard(request):
    # Logic for dashboard

# Explicit method check, if User is authenticated and has permissions to change Store model
# Explicit method with test
def user_of_stores(user):
    if user.is_authenticated() and user.has_perm("stores.change_store"):
        return True
    else:
        return False

# Method check using method
@user_passes_test(user_of_stores)
def store_manager(request):
    # Logic for store_manager

# Method check to see if User has permissions to add Store model
from django.contrib.auth.decorators import permission_required

@permission_required('stores.add_store')
def store_creator(request):
    # Logic for store_creator

Listing 10-7. Permission checks in urls.py for static templates

from django.conf.urls import  include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required,permission_required,user_passes_test
from django.contrib.auth.models import Group

urlpatterns = [
      url(r'^online/baristas/',
         user_passes_test(lambda u: Group.objects.get(name='Baristas') in u.groups.all())
         (TemplateView.as_view(template_name='online/baristas.html')),name="onlinebaristas"),      
      url(r'^online/dashboard/',
         permission_required('stores.add_store')
         (TemplateView.as_view(template_name='online/dashboard.html')),name="onlinedashboard"),
      url(r'^online/',
         login_required(TemplateView.as_view(template_name='online/index.html')),name='online'),      
]
Listing 10-8. Permission checks in urls.py for include() definitions

from django.conf.urls import include, url
from django.core.urlresolvers import RegexURLResolver, RegexURLPattern

class DecoratedURLPattern(RegexURLPattern):
    def resolve(self, *args, **kwargs):
        result = super(DecoratedURLPattern, self).resolve(*args, **kwargs)
        if result:
            result.func = self._decorate_with(result.func)
        return result

class DecoratedRegexURLResolver(RegexURLResolver):
    def resolve(self, *args, **kwargs):
        result = super(DecoratedRegexURLResolver, self).resolve(*args, **kwargs)
        if result:
            result.func = self._decorate_with(result.func)
        return result

def decorated_includes(func, includes, *args, **kwargs):
    urlconf_module, app_name, namespace = includes
    patterns = getattr(urlconf_module, 'urlpatterns', urlconf_module)    
    for item in patterns:
        if isinstance(item, RegexURLPattern):
            item.__class__ = DecoratedURLPattern
            item._decorate_with = func
            
        elif isinstance(item, RegexURLResolver):
            item.__class__ = DecoratedRegexURLResolver
            item._decorate_with = func
    return urlconf_module, app_name, namespace

from django.contrib.auth.decorators import login_required,permission_required,user_passes_test
from django.contrib.auth.models import Group
from coffeehouse.items.urls import urlpatterns as drinks_url_patterns

urlpatterns = [
    url(r'^items/', 
       decorated_includes(login_required,include(items_url_patterns,namespace="items"))),
    url(r'^stores/', 
      decorated_includes(permission_required('stores.add_store'),
      include('coffeehouse.stores.urls',namespace="stores"))),
    url(r'^social/', 
      decorated_includes(user_passes_test(lambda u: Group.objects.get(name='Baristas') in u.groups.all()),
      include('coffeehouse.social.urls',namespace="social"))),
]

Listing 10-9. Permission checks in templates

       {% if user.is_authenticated %}
          {#  Content for authenticated users  #}
       {% endif %}
       
       {% if perms.stores.add_store %}
          {#  Content for users that can add stores #}
       {% endif %}
       
       {% for group in user.groups.all %}
          {% if group.name == 'Baristas'  %}
               {# Content for users with 'Baristas' group #}
          {% endif %}
       {% endfor %}
Listing 10-10. Permission checks in class-based views

from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin

class ItemList(LoginRequiredMixin,ListView):
    model = Item
    context_object_name = 'items'
    template_name = 'items/index.html'

class ItemDetail(UserPassesTestMixin,DetailView):
    model = Item
    pk_url_kwarg = 'item_id'    
    template_name = 'items/detail.html'
    def test_func(self):
        return self.request.user.is_authenticated
    
class ItemCreation(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy('items:index')
    success_message = "Item %(name)s created successfully"
    permission_required = ('items.add_item',)

@method_decorator(login_required, name='dispatch')
class ItemUpdate(SuccessMessageMixin,UpdateView):
    model = Item
    pk_url_kwarg = 'item_id'    
    form_class = ItemForm
    success_url = reverse_lazy('items:index')
    success_message = "Item %(name)s updated successfully"

@method_decorator(user_passes_test(lambda u: Group.objects.get(name='Baristas') in u.groups.all()),
                  name='dispatch')
class ItemDelete(DeleteView):
    model = Item
    pk_url_kwarg = 'item_id'    
    success_url = reverse_lazy('items:index')

"""

