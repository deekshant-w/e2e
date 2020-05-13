# Generated by Django 3.0.6 on 2020-05-13 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_remove_message_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='read',
            field=models.DecimalField(decimal_places=0, default=0, help_text='0 => unread || 1=> read', max_digits=1),
        ),
    ]
