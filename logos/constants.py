VERSION = "0.99.6"

REDDIT_UA = "Heretical 1.0 by /u/kiwiheretic"

# Punctuation that is to be ignored when indexing words
# for concordance
PUNCTUATION = r"[\?`)(';:\*\[\],.\-\"|!\x7f]"

# stop words are words that are so common that they
# are not indexed (in the concordance).  It makes for a lot
# smaller concordance database.
STOP_WORDS = ['a', 'i', 'in', 'of', 'the', 'he', 'she',
    'and', 'said', 'be', 'it', 'was', 'is', 'on', 'to', 'you',
    'we', 'them', 'that', 'they', 'are', 'so', 'or',
    'thy', 'thou', 'her', 'his', 'him', 'there', 'their']
