from __future__ import absolute_import
from django.views.generic import DetailView
#from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import Http404
from guardian.shortcuts import get_perms

from .forms import FeedForm
from .models import MySubreddits, Subreddits, FeedSub, PendingComments, PendingSubmissions
from logos.models import RoomPermissions

# Using FormView here because CreateView seems to handle
# only saving on model instance and not a parent-children model set.
class FeedFormView(FormView):
    template_name = 'reddit/new_feed.html'
    form_class = FeedForm
    # we need to set current app but this is problematic because 
    # we dont really want it hard coded in a reusable app
    # http://stackoverflow.com/questions/2030225/how-to-get-current-app-for-using-with-reverse-in-multi-deployable-reusable-djang
    success_url = reverse_lazy('reddit:mysubreddits')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeedFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        subreddit_ids = form.cleaned_data['subreddits']
        target_sub_id = int(form.cleaned_data['target_sub'])
        target_irc_id = int(form.cleaned_data['target_irc'])
        frequency = form.cleaned_data['frequency']
        start_date = form.cleaned_data['start_date']
        post_limit = form.cleaned_data['post_limit']
        active = form.cleaned_data['active']
        if target_sub_id:
            target_sub = Subreddits.objects.get(pk=target_sub_id)
            fsub = FeedSub(user = self.request.user,
                    frequency = frequency,
                    target_sub = target_sub,
                    post_limit = post_limit,
                    start_date = start_date,
                    active = active)
            fsub.save()
        else: # Target is IRC
            target_irc = RoomPermissions.objects.get(pk=target_irc_id)
            fsub = FeedSub(user = self.request.user,
                    frequency = frequency,
                    target_irc = target_irc,
                    post_limit = post_limit,
                    start_date = start_date,
                    active = active)
            fsub.save()
        for subred_id in subreddit_ids:
            sub = Subreddits.objects.get(pk=subred_id)
            fsub.subreddits.add(sub)
        fsub.save()
        messages.add_message(self.request, messages.INFO, 'Feed record added successfully')
        return super(FeedFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FeedFormView, self).get_context_data(**kwargs)
        context.update({'heading':'New Feed'})
        return context

    def get_form_kwargs(self):
        kwargs = super(FeedFormView, self).get_form_kwargs()
        mysubs = MySubreddits.objects.get(user=self.request.user).subreddits
        choices = [(sub.pk, sub.display_name) for sub in mysubs.all()]

        irc_rooms = []
        for rp in RoomPermissions.objects.all():
            if 'room_admin' in get_perms(self.request.user, rp):
                irc_rooms.append((rp.id, rp.network + "/" + rp.room))
        kwargs.update({'mysubreddits':choices, 'myircrooms':irc_rooms})
        return kwargs



class FeedUpdateFormView(FeedFormView):
    model_class = FeedSub

    success_url = reverse_lazy('reddit:mysubreddits')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.obj_id = args[1] # skip request argument
        return super(FeedUpdateFormView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        try:
            obj = FeedUpdateFormView.model_class.objects.get(pk = self.obj_id)
            d = model_to_dict(obj)
            return d
        except FeedUpdateFormView.model_class.DoesNotExist:
            return Http404("{} does not exist".format(model_class.__name__))

    def form_valid(self, form):
        subreddit_ids = form.cleaned_data['subreddits']
        target_sub_id = int(form.cleaned_data['target_sub'])
        target_irc_id = int(form.cleaned_data['target_irc'])
        frequency = form.cleaned_data['frequency']
        start_date = form.cleaned_data['start_date']
        post_limit = form.cleaned_data['post_limit']
        active = form.cleaned_data['active']

        fsub = FeedSub.objects.get(pk=self.obj_id)
        if target_sub_id:
            target_sub = Subreddits.objects.get(pk=target_sub_id)
            fsub.target_sub = target_sub
        else:
            target_irc = RoomPermissions.objects.get(pk=target_irc_id)
            fsub.target_irc = target_irc

        fsub.subreddits.clear()
        fsub.frequency = frequency
        fsub.start_date = start_date
        fsub.post_limit = post_limit
        fsub.active = active
        fsub.save()
        for subred_id in subreddit_ids:
            sub = Subreddits.objects.get(pk=subred_id)
            fsub.subreddits.add(sub)
        fsub.save()
        messages.add_message(self.request, messages.INFO, 'Feed record updated successfully')
        return super(FormView, self).form_valid(form)

class RedditListView(ListView):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RedditListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(RedditListView, self).get_context_data(**kwargs)
        ctx.update(self.context)
        return ctx

class CommentsListView(RedditListView):
    model = PendingComments
    template_name = "reddit/pending_comments.html"
    context = {'title':'Pending Comments'}

class CommentsDeleteView(DeleteView):
    model = PendingComments
    success_url = reverse_lazy('reddit:pending_comments')

class SubmissionsListView(RedditListView):
    model = PendingSubmissions
    template_name = "reddit/pending_posts.html"
    context = {'title':'Pending Submissions'}
