# Generated by Django 3.0.6 on 2020-05-14 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timeStamp', models.DateTimeField(auto_now_add=True)),
                ('fromTo', models.DecimalField(decimal_places=0, help_text='1 => a->b || 2=> b->a', max_digits=1)),
                ('read', models.DecimalField(decimal_places=0, default=0, help_text='0 => unread || 1=> read', max_digits=1)),
                ('msg', models.TextField()),
            ],
        ),
    ]
