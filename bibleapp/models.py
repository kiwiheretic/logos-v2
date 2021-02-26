from django.db import models

DB_ROUTER={"bibles":('BibleTranslations', 'BibleBooks', 
                  'BibleVerses', 'BibleConcordance', 
                  'BibleDict', 'XRefs')}

class BibleColours(models.Model):
    network = models.TextField()
    room = models.TextField()
    element = models.TextField()
    mirc_colour = models.TextField()
    class Meta:
        db_table = 'bible_colours'
        # app_label = 'logos'

class XRefs(models.Model):
    primary_book = models.CharField(max_length = 15)
    primary_chapter = models.IntegerField()
    primary_verse = models.IntegerField()
    xref_book1 = models.CharField(max_length = 15)
    xref_chapter1 = models.IntegerField()
    xref_verse1 = models.IntegerField()
    xref_book2 = models.CharField(max_length = 15, null = True, blank = True)
    xref_chapter2 = models.IntegerField(null = True, blank = True)
    xref_verse2 = models.IntegerField(null = True, blank = True)
    votes = models.IntegerField()
    class Meta:
        # app_label = 'logos'
        db_table = 'xrefs'


class BibleTranslations(models.Model):
    name = models.CharField(unique=True, max_length=10)
    class Meta:
        db_table = 'bible_translations'
        # app_label = 'logos'

class BibleBooks(models.Model):
    trans = models.ForeignKey('BibleTranslations', on_delete=models.CASCADE)
    book_idx = models.IntegerField()
    long_book_name = models.TextField()
    canonical = models.TextField(blank=True)
    class Meta:
        db_table = 'bible_books'
        # app_label = 'logos'

class BibleVerses(models.Model):
    trans = models.ForeignKey('BibleTranslations', on_delete=models.CASCADE)
    book = models.ForeignKey('BibleBooks', on_delete=models.CASCADE)
    chapter = models.IntegerField()
    verse = models.IntegerField()
    verse_text = models.TextField()
    class Meta:
        # app_label = 'logos'
        db_table = 'bible_verses'
        index_together = [
            ["trans", "book", "chapter", "verse"],
        ]

class BibleStats(models.Model):
    trans_idx = models.IntegerField()
    word = models.CharField(max_length=60)
    count = models.IntegerField()
    class Meta:
        # app_label = 'logos'    
        index_together = [
            ["trans_idx", "count"],
        ]  
      
class BibleConcordance(models.Model):
    trans = models.ForeignKey('BibleTranslations', on_delete=models.CASCADE)
    book = models.ForeignKey('BibleBooks', on_delete=models.CASCADE)
    chapter = models.IntegerField()
    verse = models.IntegerField()
    word_id = models.IntegerField()
    word = models.CharField(max_length=60)
    class Meta:
        # app_label = 'logos'
        db_table = 'bible_concordance'
        index_together = [
            ["trans", "book", "chapter", "verse", "word_id"],
            ["trans", "word"],
            ["trans", "word", "chapter"],
            ["trans", "word", "chapter", "verse"],
        ]

class BibleDict(models.Model):
    strongs = models.CharField(db_index=True, max_length=10)
    description = models.TextField(blank=True)
    class Meta:
        # app_label = 'logos'
        db_table = 'bible_dict'


