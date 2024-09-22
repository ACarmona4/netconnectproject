from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from company.models import Company

@receiver(post_save, sender=User)
def create_company_for_user(sender, instance, created, **kwargs):
    if instance.is_company:
        if not Company.objects.filter(email=instance.email).exists():
            Company.objects.create(
                id=instance.id,
                logo=instance.logo,
                name=instance.name,
                description=f'Pendiente por definir',
                email=instance.email,
                personInCharge=f'pendiente por definir'
            )