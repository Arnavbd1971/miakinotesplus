from django.db import models
from django import forms
from django.shortcuts import redirect
from django.utils.text import slugify
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.core.signing import Signer
from django.utils.html import mark_safe
import markdown
import uuid
from django.urls import reverse
from unidecode import unidecode
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
import markdown.extensions.tables
import markdown.extensions.toc
from django_cryptography.fields import encrypt
from ckeditor.fields import RichTextField


def generate_unique_slug(_class, field):
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    while _class.objects.filter(slug=unique_slug).exists():
        unique_slug = '%s-%d' % (origin_slug, numb)
        numb += 1
    return unique_slug



class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note_title = models.CharField(max_length=200)
    note_content = encrypt(RichTextField(null=True, blank=True))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=200, unique=True)
    tags = TaggableManager()
    signer = Signer(salt='notes.Note')

    def get_message_as_markdown(self):
        return mark_safe(
            markdown.markdown(
                self.note_content,
                extensions=['codehilite', 'fenced_code', 'markdown_checklist.extension', 'tables', 'toc'],
                output_format="html5"
            )
        )

    def get_signed_hash(self):
        signed_pk = self.signer.sign(self.pk)
        return signed_pk

    def get_absolute_url(self):
        return reverse('share_notes', args=(self.get_signed_hash(),))

    def __str__(self):
        return self.note_title

    def save(self, *args, **kwargs):
        title = unidecode(self.note_title)
        if self.slug:
            if slugify(title) != self.slug:
                self.slug = generate_unique_slug(Note, title)
        else:
            self.slug = generate_unique_slug(Note, title)
        super(Note, self).save(*args, **kwargs)


class AddNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = '__all__'
        exclude = ['slug', 'user']
        widgets = {
            'tags': forms.TextInput(
                attrs={
                    'data-role':'tagsinput',
                }
            ),
        }

class Share(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, null=True, blank=True)
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2user', null=True, blank=True)
    user_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=200, unique=True, default=0)
    view_status = models.CharField(max_length=100, default='pendding')

    def save(self, *args, **kwargs):
        note = self.note
        if self.slug:
            if slugify(note) != self.slug:
                self.slug = generate_unique_slug(Share, note)
        else:
            self.slug = generate_unique_slug(Share, note)

        Notification.objects.create(notification_type=1, from_user=self.user_by, to_user=self.user_to, note=self.note)

        super(Share, self).save(*args, **kwargs)

class ShareNoteForm(forms.ModelForm):
    class Meta:
        model = Share
        fields = '__all__'
        exclude = ['note', 'user_by', 'slug', 'view_status']

class Notification(models.Model):
	# 1 = share,
	notification_type = models.IntegerField()
	to_user = models.ForeignKey(User, related_name='notification_to', on_delete=models.CASCADE, null=True)
	from_user = models.ForeignKey(User, related_name='notification_from', on_delete=models.CASCADE, null=True)
	note = models.ForeignKey('Note', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
	share = models.ForeignKey('Share', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
	date = models.DateTimeField(auto_now=True)
	user_has_seen = models.BooleanField(default=False)
	mail_sent_status = models.BooleanField(default=False)


# mail_sent_status