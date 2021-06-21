from django.shortcuts import render,redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
#Authentication mixins
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import Http404
from .models import Task
# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('tasks')

    def form_valid(self, form): #Once the post request is sent, this runs
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)
    

#A viewset could do all these CRUD requests by default.

class TaskList(LoginRequiredMixin, ListView): #Inherits from listview
    #Returns a template of a queryset of data
    model = Task
    context_object_name = 'tasks'
    #Classbased views automatically find the template give the model
    # the template name is <model>_list.html

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # Context is a dictionary
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        #Sets the tasks to show only the ones that are made by the user
        context['count'] =  context['tasks'].filter(complete=False).count()
        #Holds the count of incomplete items

        search_input = self.request.GET.get('search-area') #Get the input from the search-area text box input
        if search_input:
            context['tasks'] = context['tasks'].filter(title__icontains=search_input)
            context['search_input'] = search_input
        else:
            context['search_input'] = ''
        return context
        

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    #the default template name is <model>_detail.html
    template_name='base/task.html' #Change the template name that it looks for

class TaskCreate(LoginRequiredMixin, CreateView): #Does the GET and POST CRUD actions.
    model = Task
    fields = ['title','description','complete']
    success_url = reverse_lazy('tasks') #redirects the user to the task list

    def form_valid(self, form):
        form.instance.user = self.request.user 
        #Makes it so the user can only pick themselves as a user for their task
        return super(TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView): #Does the PUT CRUD action.
    model = Task
    fields = ['title','description','complete']
    success_url = reverse_lazy('tasks') #redirects the user to the task list
    #<model>_form.html

class TaskDelete(LoginRequiredMixin, DeleteView): #Does the DELETE CRUD action.
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks') #redirects the user to the task list
    #The default template name is <model>_confirm_delete.html

