import datetime
from haystack import indexes
from .models import Note


class NoteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created_date = indexes.DateTimeField(model_attr='created_at')
    # Even though User is a foreign key it seems to have to be a CharField
    # as IntegerField causes weird incomprehensible errors.
    # However this field needs to be here so we can filter the results
    # in the haystack queryset by user.
    user = indexes.CharField(model_attr='user')
    body = indexes.CharField(model_attr='note')
    
    def get_model(self):
        return Note

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.exclude(folder__name = 'Trash')
