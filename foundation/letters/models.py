import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from model_utils.managers import PassThroughManager
from model_utils.models import TimeStampedModel
from autoslug.fields import AutoSlugField
from django.core.files.base import ContentFile
from django_bleach.models import BleachField
from foundation.offices.models import Office
from django.db.models.signals import pre_save
from django.utils import timezone
from .email import MessageTemplateEmail


INCOMING_HELP = _("Is it a incoming message? Otherwise, it is outgoing.")


class LetterQuerySet(models.QuerySet):
    pass


class Letter(TimeStampedModel):
    # General
    case = models.ForeignKey('cases.Case')
    subject = models.CharField(verbose_name=_("Subject"), max_length=50)
    slug = AutoSlugField(populate_from='subject', verbose_name=_("Slug"), unique=True)
    content = BleachField()
    incoming = models.BooleanField(default=False, verbose_name=_("Incoming"),
                                   help_text=INCOMING_HELP)
    eml = models.FileField(upload_to="eml_msg/%Y/%m/%d/", null=True, blank=True)
    # Outgoing
    sender_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    send_at = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name="author_letter",
                               null=True,
                               blank=True)
    email = models.ForeignKey('offices.Email', null=True, blank=True)
    # Incoming
    sender_office = models.ForeignKey(Office, null=True, blank=True, related_name='sender_office')
    from_email = models.CharField(verbose_name=_("From e-mail"),
                                  max_length=100,
                                  null=True,
                                  help_text=_("Field valid only for incoming messages"))
    objects = PassThroughManager.for_queryset_class(LetterQuerySet)()

    def recipient(self):
        return self.email.office

    @property
    def sender(self):
        return self.sender_user or self.sender_office

    @sender.setter
    def sender(self, value):
        if isinstance(value, Office):
            self.sender_office = value
            self.sender_user = None
        else:
            self.sender_user = value
            self.sender_office = None

    def is_send(self):
        return bool(self.eml)

    class Meta:
        verbose_name = _("Letter")
        verbose_name_plural = _("Letters")
        ordering = ['created', ]

    def __unicode__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('letters:details', kwargs={'slug': self.slug})

    def send(self, user):
        text = self.content.replace('{{EMAIL}}', self.case.receiving_email)
        to = self.email.email
        # Construct MimeText instance
        context = dict(text=text,
                       office=self.email.office,
                       case=self.case,
                       letter=self,
                       email=self.case.receiving_email)
        msg = MessageTemplateEmail().make_email_object(to=to,
                                                       context=context)
        msg.extra_headers.update({'Return-Receipt-To': self.case.receiving_email,
                                  'Disposition-Notification-To': self.case.receiving_email})
        msg.from_email = self.case.receiving_email
        # Save MimeText to file
        self.eml.save('%s.eml' % uuid.uuid4(),
                      ContentFile(msg.message().as_string()),
                      save=False)
        # Update instance
        self.sender_user = user
        self.incoming = False
        # Save instance
        self.save()
        # Send message
        msg.send()


def update_send_at(sender, instance, **kwargs):
    if (not instance.incoming and  # outgoing
            not instance.send_at and  # no send time
            instance.eml):  # send msg set up
        instance.send_at = timezone.now()

pre_save.connect(update_send_at, sender=Letter, dispatch_uid="update_send_at")
