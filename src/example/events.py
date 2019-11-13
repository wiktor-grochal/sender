from nameko.standalone.events import event_dispatcher
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RegularModel
from django.core import serializers
import json

AMQP_URI = 'pyamqp://guest:guest@172.17.0.5'
AMQP_CONFIG = {
    'AMQP_URI': AMQP_URI
}

dispatch = event_dispatcher(AMQP_CONFIG)


# TODO dorobić walidację list modeli które są syncowane w 2 appkach i jak gdzieś sie nie zgadza to dac warna
# TODO wyścig przy drzewie
@receiver(post_save, sender=RegularModel)
def regularmodel_saved(sender, instance, created, **kwargs):
    payload = serializers.serialize("python", [instance, ])[0]
    payload = json.dumps(payload)
    # case is important
    dispatch("example_sender", "RegularModel_saved", payload)

