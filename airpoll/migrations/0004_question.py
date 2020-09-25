# Generated by Django 3.1.1 on 2020-09-25 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('airpoll', '0003_survey'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Text')),
                ('order', models.IntegerField(verbose_name='Order')),
                ('required', models.BooleanField(verbose_name='Required')),
                ('type', models.CharField(choices=[('text', 'text (multiple line)'), ('short-text', 'short text (one line)'), ('radio', 'radio'), ('select', 'select'), ('select-multiple', 'Select Multiple'), ('select_image', 'Select Image'), ('integer', 'integer'), ('float', 'float'), ('date', 'date')], default='text', max_length=200, verbose_name='Type')),
                ('choices', models.TextField(blank=True, help_text="The choices field is only used if the question type\nif the question type is 'radio', 'select', or\n'select multiple' provide a comma-separated list of\noptions for this question .", null=True, verbose_name='Choices')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='airpoll.survey', verbose_name='Survey')),
            ],
            options={
                'verbose_name': 'question',
                'verbose_name_plural': 'questions',
                'ordering': ('survey', 'order'),
            },
        ),
    ]