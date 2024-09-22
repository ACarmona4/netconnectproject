# Generated by Django 5.1.1 on 2024-09-22 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0004_delete_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('logo', models.ImageField(default='company/images/default.jpg', upload_to='company/images/')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=300)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=15)),
                ('personInCharge', models.CharField(max_length=100)),
            ],
        ),
    ]
