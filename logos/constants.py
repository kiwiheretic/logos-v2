VERSION = "0.98.12"

PUNCTUATION = r"[\?`)(';:\*\[\],.\-\"|!\x7f]"

# stop words are words that are so common that they
# are not indexed (in the concordance).  It makes for a lot
# smaller concordance database.
STOP_WORDS = ['a', 'i', 'in', 'of', 'the', 'he', 'she',
    'and', 'said', 'be', 'it', 'was', 'is', 'on', 'to',
    'thy', 'thou', 'her', 'his', 'him', 'there', 'their']
