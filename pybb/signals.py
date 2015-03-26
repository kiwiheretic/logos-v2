from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F, Count

from pybb.models import Forum, Topic, Post

@receiver(post_save, sender=Topic)
def topic_post_save(instance, **kwargs):
    topic = instance
    topic_count = topic.forum.topics.count()
    Forum.objects.filter(pk=topic.forum_id)\
         .update(topic_count=topic_count)


@receiver(post_save, sender=Post)
def post_post_save(instance, **kwargs):
    post = instance
    topic = post.topic
    topic_post_count = topic.posts.count()
    forum_post_count = Post.objects.filter(topic__forum=topic.forum)\
                           .aggregate(num=Count('pk'))['num']
    Topic.objects.filter(pk=post.topic_id)\
         .update(post_count=topic_post_count)
    Forum.objects.filter(pk=topic.forum_id)\
         .update(post_count=forum_post_count)


@receiver(post_delete, sender=Topic)
def topic_post_delete(instance, **kwargs):
    topic = instance
    topic_count = topic.forum.topics.count()
    post_count = Post.objects.filter(topic__forum=topic.forum)\
                     .aggregate(num=Count('pk'))['num']
    Forum.objects.filter(pk=topic.forum_id)\
         .update(topic_count=topic_count,
                 post_count=post_count)
