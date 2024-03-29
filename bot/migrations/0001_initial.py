# Generated by Django 4.0.1 on 2023-03-17 11:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TgUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_chat_id', models.BigIntegerField(unique=True, verbose_name='Чат Телеграм')),
                ('verification_code', models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='Код верификации пользователя')),
                ('tg_username', models.CharField(blank=True, default=None, max_length=40, null=True, unique=True, verbose_name='Пользователь Телеграм')),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Пользователь Телеграм',
                'verbose_name_plural': 'Пользователи Телеграм',
                'ordering': ['-id'],
            },
        ),
    ]
