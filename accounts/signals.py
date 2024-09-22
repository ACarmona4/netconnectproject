from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from company.models import Company

@receiver(post_save, sender=User)
def create_company_for_user(sender, instance, created, **kwargs):
    if instance.is_company:
        if created:
            Company.objects.create(
                user=instance,
                logo=instance.logo,
                name=instance.name,
                description='Pendiente por definir',
                email=instance.email,
                personInCharge='Pendiente por definir'
            )
        else:
            if hasattr(instance, 'company'):
                company = instance.company
                company.logo = instance.logo
                company.name = instance.name
                company.email = instance.email
                company.save()