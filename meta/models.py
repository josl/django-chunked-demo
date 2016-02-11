from django.db import models
from django.conf import settings
import uuid

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
# Create your models here.


def generate_id():
    return uuid.uuid4().hex


class Metadata(models.Model):
    '''
    MetaData model.
    '''

    class Meta:
        abstract = False

    PLATFORM = (
        ('Illumina', 'Illumina'),
        ('Ion Torrent', 'Ion Torrent'),
    )
    SEQ_TYPE = (
        ('single', 'single'),
        ('paired', 'paired'),
        ('mate-paired', 'mate-paired'),
        ('unknown', 'unknown'),
    )
    PRE_ASSEMBLED = (
        ('yes', 'yes'),
        ('no', 'no'),
    )
    SOURCE = (
        ('human', 'human'),
        ('water', 'water'),
        ('food', 'food'),
        ('animal', 'animal'),
        ('other', 'other'),
        ('laboratory', 'laboratory'),
    )
    PATHO = (
        ('yes', 'yes'),
        ('no', 'no'),
        ('unknown', 'unknown'),
    )
    RESTRICTION = (
        ('private', 'private'),
        ('public', 'public'),
    )
    DATE_FORMATS = [
      '%Y-%m-%d',  # '2006-10-25'
      '%Y-%m',     # '2006-10'
      '%Y']        # '2006'

    meta_id = models.CharField(max_length=32, unique=True, editable=False,
                               default=generate_id)
    uid = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)

    sequencing_platform = models.CharField(max_length=255, choices=PLATFORM)
    sequencing_type = models.CharField(max_length=255, choices=SEQ_TYPE)
    pre_assembled = models.CharField(max_length=255, choices=PRE_ASSEMBLED)
    isolation_source = models.CharField(max_length=255, choices=SOURCE)

    pathogenic = models.CharField(max_length=255, choices=PATHO, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    sample_name = models.CharField(max_length=255, null=True)
    longitude = models.CharField(max_length=255, null=True)
    latitude = models.CharField(max_length=255, null=True)
    # longitude = models.DecimalField(max_digits=8, decimal_places=3,
    #                                 null=True)
    # latitude = models.DecimalField(max_digits=8, decimal_places=3,
    #                                null=True)
    organism = models.CharField(max_length=255, null=True)
    strain = models.CharField(max_length=255, null=True)
    subtype = models.CharField(max_length=255, null=True)

    country = models.CharField(max_length=255)

    region = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=255, null=True)
    location_note = models.CharField(max_length=255, null=True)
    source_note = models.CharField(max_length=255, null=True)
    pathogenicity_note = models.CharField(max_length=255, null=True)
    collected_by = models.CharField(max_length=255, null=True)
    email_address = models.EmailField(max_length=255, null=True)
    notes = models.TextField(max_length=255, null=True)

    collection_date = models.CharField(max_length=255)
    release_date = models.EmailField(max_length=255, null=True)
    # collection_date = models.DateField(max_length=255
    #                                    # , input_formats=DATE_FORMATS
    #                                    )
    #
    # release_date = models.DateField(max_length=255,
    #                                 # input_formats=DATE_FORMATS,
    #                                 null=True)
