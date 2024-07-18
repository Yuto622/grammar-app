from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser


class Chart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    duration = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    sentence_count = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)

    @classmethod
    def create_chart(cls, user, duration,  error_count, sentence_count, word_count, **extra_fields):

        if not user:
            raise ValueError(_("The user must be set"))
        chart = cls(user=user, duration=duration, error_count=error_count, sentence_count=sentence_count, word_count=word_count, **extra_fields)
        chart.save()
        return chart

    def __str__(self):
        return self.id
