from __future__ import absolute_import
from django.views.generic import DetailView
#from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .forms import FeedForm
from .models import MySubreddits, Subreddits, FeedSub
# Using FormView here because CreateView seems to handle
# only saving on model instance and not a parent-children model set.
class SubredditFeedFormView(FormView):
    template_name = 'reddit/new_feed.html'
    form_class = FeedForm
    # we need to set current app but this is problematic because 
    # we dont really want it hard coded in a reusable app
    # http://stackoverflow.com/questions/2030225/how-to-get-current-app-for-using-with-reverse-in-multi-deployable-reusable-djang
    success_url = reverse_lazy('reddit:mysubreddits')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        subreddit_ids = form.cleaned_data['subreddits']
        target = form.cleaned_data['target']
        frequency = form.cleaned_data['frequency']
        active = form.cleaned_data['active']
        target_sub = Subreddits.objects.get(pk=target)
        fsub = FeedSub(user = self.request.user,
                frequency = frequency,
                target_sub = target_sub,
                active = active)
        fsub.save()
        for subred_id in subreddit_ids:
            sub = Subreddits.objects.get(pk=subred_id)
            fsub.subreddits.add(sub)
        fsub.save()
        messages.add_message(self.request, messages.INFO, 'Feed record added successfully')
        return super(self.__class__, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(SubredditFeedFormView, self).get_context_data(**kwargs)
        context.update({'heading':'New Subreddit Feed'})
        return context

    def get_form_kwargs(self):
        kwargs = super(SubredditFeedFormView, self).get_form_kwargs()
        mysubs = MySubreddits.objects.get(user=self.request.user).subreddits
        choices = [(sub.pk, sub.display_name) for sub in mysubs.all()]
        kwargs.update({'mysubreddits':choices})
        return kwargs

class IRCFeedFormView(FormView):
    template_name = 'reddit/new_feed.html'
    form_class = FeedForm
    success_url = '/thanks/'

    def form_valid(self, form):
        pass

    def get_context_data(self, **kwargs):
        context = super(IRCFeedFormView, self).get_context_data(**kwargs)
        context.update({'heading':'New IRC Feed'})
        return context

    def get_form_kwargs(self):
        kwargs = super(IRCFeedFormView, self).get_form_kwargs()
        mysubs = MySubreddits.objects.get(user=self.request.user).subreddits
        choices = [(sub.pk, sub.display_name) for sub in mysubs.all()]
        kwargs.update({'mysubreddits':choices})
        return kwargs



