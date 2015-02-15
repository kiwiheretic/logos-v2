from django.db import models

DB_ROUTER="bibles"

class BibleTranslations(models.Model):
    name = models.CharField(unique=True, max_length=10)
    class Meta:
        db_table = 'bible_translations'

class BibleBooks(models.Model):
    trans = models.ForeignKey('BibleTranslations')
    book_idx = models.IntegerField()
    long_book_name = models.TextField()
    canonical = models.TextField(blank=True)
    class Meta:
        db_table = 'bible_books'

class BibleVerses(models.Model):
    trans = models.ForeignKey('BibleTranslations')
    book = models.ForeignKey('BibleBooks')
    chapter = models.IntegerField()
    verse = models.IntegerField()
    verse_text = models.TextField()
    class Meta:
        db_table = 'bible_verses'
        index_together = [
            ["trans", "book", "chapter", "verse"],
        ]

class BibleConcordance(models.Model):
    trans = models.ForeignKey('BibleTranslations')
    book = models.ForeignKey('BibleBooks')
    chapter = models.IntegerField()
    verse = models.IntegerField()
    word_id = models.IntegerField()
    word = models.CharField(max_length=60)
    class Meta:
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
        db_table = 'bible_dict'


