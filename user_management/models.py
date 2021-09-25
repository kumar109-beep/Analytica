from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User
from django.dispatch import receiver


class UserProfile(models.Model):
    user   = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='images', null=True, blank=True)

    @property
    def avatar_with_default(self):
        return self.avatar or "images/default_avtar.png"


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile, sender=User)



@receiver(models.signals.pre_save, sender=UserProfile)
def delete_file_on_change_extension(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_avatar = UserProfile.objects.get(pk=instance.pk).avatar
        except UserAccount.DoesNotExist:
            return
        else:
            new_avatar = instance.avatar
            if old_avatar and old_avatar.url != new_avatar.url:
                old_avatar.delete(save=False)
