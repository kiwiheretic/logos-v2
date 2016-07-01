from __future__ import absolute_import
from django.views.generic import DetailView
#from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse_lazy
from .forms import NewSubredditFeedForm
from .models import MySubreddits
# Using FormView here because CreateView seems to handle
# only saving on model instance and not a parent-children model set.
class FeedFormView(FormView):
    template_name = 'reddit/new_feed.html'
    form_class = NewSubredditFeedForm
    success_url = '/thanks/'

    def form_valid(self, form):
        pass

    def get_form_kwargs(self):
        kwargs = super(FeedFormView, self).get_form_kwargs()
        mysubs = MySubreddits.objects.get(user=self.request.user).subreddits
        choices = [(sub.pk, sub.display_name) for sub in mysubs.all()]
        kwargs.update({'mysubreddits':choices})
        return kwargs




