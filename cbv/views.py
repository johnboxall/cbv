from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.defaults import page_not_found
from django.core.urlresolvers import reverse

from .models import User
from .forms import UserForm


###
# Functional Style Views
###

# Template Views
def home(request, template_name="base.html"):
    import pdb;pdb.set_trace()
    return render(request, template_name)

def about(request, template_name="about.html"):
    return render(request, template_name)

def handler404(request, template_name='404.html'):
    return page_not_found(request, template_name)

# Detail Views
def user_detail(request, pk, template_name="user_detail.html"):
    user = get_object_or_404(User, pk=pk)

    context = {
        "user": user
    }

    return render(request, template_name, context)

# List Views
def user_list(request, template_name="user_list.html"):
    users = User.objects.all()

    context = {
        "users": users
    }

    return render(request, template_name, context)

# Form Views
def user_create(request, template_name="user_create.html"):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        next = reverse("user_detail", args=(user.pk,))
        return HttpResponseRedirect(next)

    context = {
        "form": form
    }

    return render(request, template_name, context)

def user_edit(request, pk, template_name="user_edit.html"):
    user = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        next = "."
        return HttpResponseRedirect(next)

    context = {
        "form": form
    }

    return render(request, template_name, context)


###
# Class Based Views
###

from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
                                    DeleteView, TemplateView, FormView, View

# Template Views
class Home(TemplateView):
    template_name = "base.html"

    # def post(self, *args, **kwargs):
    #     import pdb;pdb.set_trace()
    #     return super(Home, self).post(*args, **kwargs)


    # def get(self, *args, **kwargs):
    #     import pdb;pdb.set_trace()
    #     return super(Home, self).get(*args, **kwargs)



def handler404(request, template_name='404.html'):
    return page_not_found(request, template_name)

class About(TemplateView):
    template_name = "about.html"

class FourOhFour(View):
    def get(self, *args, **kwargs):
        return handler404(self.request)
        # return page_not_found(self.request, "404.html")

# Detail Views
class UserDetail(DetailView):
    model = User
    template_name = "user_detail.html"

# List Views
class UserList(ListView):
    model = User
    template_name = "user_list.html"
    context_object_name = "users"

# Form Views
class UserCreate(CreateView):
    model = User
    form = UserForm
    template_name = "user_create.html"
    success_url = "/user/detail/%(id)s"

class UserEdit(UpdateView):
    model = User
    form = UserForm
    template_name = "user_edit.html"
    success_url = "."



###
# More Advanced
###

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


###
# Decorators
###

class StaffRequiredMixin(object):
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


class StaffRequiredHome(StaffRequiredMixin, Home):
    pass


###
# Mixins
###

class MessageMixin(object):
    def message(self, message, status=messages.SUCCESS):
        messages.add_message(self.request, status, message)

    def form_valid(self, form):
        if hasattr(self, 'message_valid'):
            message = self.message_valid % form.cleaned_data
            self.message(message)
        return super(MessageMixin, self).form_valid(form)

    def form_invalid(self, form):
        if hasattr(self, 'message_invalid'):
            message = self.message_invalid
            self.message(message)
        return super(MessageMixin, self).form_invalid(form)


class MessageUserCreate(MessageMixin, UserCreate):
    message_valid = 'User Created! GJ.'
    success_url = "/"


class MessageUserEdit(MessageMixin, UserEdit):
    message_valid = 'YOU THE BEST'
    message_invalid = 'TRY AGAIN. :('





###
# Exposed View
#
# This requires some magic-machinery to work: a decorator, a wrapper, and a metaclass.
###

class ExposedProperty(object):
    '''
    Wraps a property with this class. The `prop` will be unwrapped before
    the class is initialized. It is only used to signify to the metaclass
    it should be exposed.

    '''
    def __init__(self, prop):
        self.prop = prop

    def __get__(self, *args, **kwargs):
        return self.prop.__get__(*args, **kwargs)

    def __set__(self, *args, **kwargs):
        return self.prop.__set__(*args, **kwargs)

    def __delete__(self, *args, **kwargs):
        return self.prop.__delete__(*args, **kwargs)


def expose(fn):
    return ExposedProperty(fn)


class ExposedMetaclass(type):
    '''
    ExposedMetaclass is a view-metaclass that looks for properties that have
    been decorated with `expose`. It then places their names in to the class
    attribute `exposed`.

    '''
    def __new__(cls, classname, bases, dct):
        '''
        Runs when a class (not an instance) is declared.

        '''

        # Get our classes exposed properties.
        exposed = set(dct.get('exposed', []))

        # Decorator
        for prop, value in dct.iteritems():
            if isinstance(value, ExposedProperty):
                exposed.add(prop)

        # Get superclasses exposed properties
        for base in bases:
            for prop in getattr(base, 'exposed', []):
                exposed.add(prop)

            # Decorators
            for prop, value in base.__dict__.iteritems():
                if isinstance(value, ExposedProperty):
                    exposed.add(prop)

        dct['exposed'] = list(exposed)
        return type.__new__(cls, classname, bases, dct)


class ExposedMixin(object):
    '''
    ExposedMixin allows you to use the decorator `@expose` to mark
    methods to be exposed in the template context.

    '''
    __metaclass__ = ExposedMetaclass

    exposed = ()

    def get_context_data(self, **kwargs):
        context = super(ExposedMixin, self).get_context_data(**kwargs)
        context.update(self.get_exposed_properties())
        return context

    def get_exposed_properties(self):
        properties = {}
        for prop in self.exposed:
            properties[prop] = getattr(self, prop)
        return properties



###
# Composite View
###






class CompositeView(TemplateView):
    '''
    Allows complex class based views to created by composing number of class
    based views.

    '''
    views = None

    def dispatch_to_view(self, view_cls, *args, **kwargs):
        view_instance = view_cls()
        view_instance.request = self.request
        view_instance.args = args
        view_instance.kwargs = kwargs

        # Method override
        method = kwargs.pop('method', self.request.method)
        _method = self.request.method
        self.request.method = method.upper()

        if method.lower() in self.http_method_names:
            handler = getattr(view_instance, method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        response = handler(self.request, *args, **kwargs)
        self.request.method = _method
        return response

    def get(self, *args, **kwargs):
        '''
        Respond using the combined context of the composed views.
        Short circuit if any of the views return a non-200 status code.

        '''
        combined_context = {}

        for view_name, view_cls in self.views.items():
            response = self.dispatch_to_view(view_cls, *args, **kwargs)
            if response.status_code != 200:
                return response

            combined_context[view_name] = response.context_data

        combined_context.update(self.get_context_data(params=kwargs))
        response = self.render_to_response(combined_context)
        return response

    def post(self, *args, **kwargs):
        '''
        Route the request to the requested view using the `view_name` key.
        Short circuit if it returns a non-200 status code otherwise respond
        using the combined context of the composed views.

        '''
        view_name = self.request.POST['view_name']
        views = self.views.copy()
        view_cls = views.pop(view_name)

        response = self.dispatch_to_view(view_cls, *args, **kwargs)
        if response.status_code != 200:
            return response

        combined_context = {view_name: response.context_data}

        # Fake `GET` to other views.
        for view_name, view_cls in views.items():
            response = self.dispatch_to_view(view_cls, *args, method='get', **kwargs)
            if response.status_code != 200:
                return response

            combined_context[view_name] = response.context_data

        combined_context.update(self.get_context_data(params=kwargs))
        response = self.render_to_response(combined_context)
        return response


class UserListUserCreate(CompositeView):
    views = {
        'user_list': UserList,
        'user_create': UserCreate
    }

    template_name = 'user_list_user_create.html'