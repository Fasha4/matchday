# Generated by Django 5.1.7 on 2025-03-07 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_matchday', models.CharField(max_length=255)),
                ('name_onefootball', models.CharField(max_length=255)),
                ('name_fifa', models.CharField(max_length=255)),
                ('name_viaplay', models.CharField(max_length=255)),
                ('name_apple', models.CharField(max_length=255)),
                ('name_polsat', models.CharField(max_length=255)),
            ],
        ),
    ]
