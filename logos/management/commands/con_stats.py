from django.core.management.base import BaseCommand, CommandError

# reset_queries, workaround for MemoryError when working with large databases 
# See http://travelingfrontiers.wordpress.com/2010/06/26/django-memory-error-how-to-work-with-large-databases/
# and https://docs.djangoproject.com/en/dev/faq/models/#why-is-django-leaking-memory
from django.db import reset_queries


from plugins.bible.models import BibleConcordance, BibleStats
import gc

def queryset_iterator(queryset, chunksize=1000):
    '''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()

class Command(BaseCommand):
#    args = '<poll_id poll_id ...>'
#    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        largs = list(args)
        self.stdout.write("Running concordance stats")

        BibleStats.objects.all().delete()
        conc_recs = queryset_iterator(BibleConcordance.objects.order_by('trans'))
        idx = 0
        for rec in conc_recs:
            trans_idx = rec.trans.id
            bs, created = BibleStats.objects.get_or_create(defaults = {'count':1},
                                                  trans_idx = trans_idx,
                                                  word = rec.word)
            if not created:
                bs.count += 1
                bs.save() 
            if idx % 200 ==0: 
                print "xxx", rec.word
                reset_queries()
            idx += 1
        