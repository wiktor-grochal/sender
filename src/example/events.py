from decimal import Decimal
from nameko.standalone.events import event_dispatcher
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RegularModel
from django.core import serializers
import json
import datetime

# TODO dorobić walidację list modeli które są syncowane w 2 appkach i jak gdzieś sie nie zgadza to dac warna
# TODO wyścig przy drzewie
AMQP_URI = 'pyamqp://guest:guest@172.17.0.5'
AMQP_CONFIG = {
    'AMQP_URI': AMQP_URI
}

dispatch = event_dispatcher(AMQP_CONFIG)


class DateTimeDecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        return super(DateTimeDecimalEncoder, self).default(obj)


encoder = DateTimeDecimalEncoder()


@receiver(post_save, sender=RegularModel)
def regularmodel_saved(sender, instance, created, **kwargs):
    payload = serializers.serialize("python", [instance, ])[0]
    payload = encoder.encode(payload)
    # case is important
    dispatch("example_sender", "RegularModel_saved", payload)

