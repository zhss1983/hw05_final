# Generated by Django 2.2.6 on 2021-07-05 12:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20210531_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(blank=True, help_text='Тема групп. Можно не выбирать.', null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(help_text='Адрес по которому можно будет обратиться и посмотреть записи в группе. Можно не выбирать. Есть автозаполнение.', unique=True, verbose_name='Адрес группы'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Название тематической группы. Обязательно к заполнению. Применяется для автоматического заполнения slug адреса', max_length=200, unique=True, verbose_name='Имя группы'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Тематическая группа. Группы создают администраторы. Можно не выбирать.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Текст вашего поста.', verbose_name='Текст'),
        ),
    ]
