

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Destination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('code', models.CharField(blank=True, db_index=True, max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('code', models.CharField(blank=True, db_index=True, max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransportType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(default=0)),
                ('longitude', models.FloatField(default=0)),
                ('description', models.TextField(max_length=255)),
                ('weight_capacity', models.FloatField(default=0)),
                ('currnt_weight_capacity', models.FloatField(default=0)),
                ('code', models.CharField(max_length=50)),
                ('inTrancport', models.BooleanField(default=False)),

                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('owner', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=250)),
                ('price', models.IntegerField()),
                ('weight', models.FloatField()),
                ('receivedDate', models.DateField()),
                ('inContainer', models.BooleanField(default=False)),
                ('container', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main_app.container')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, choices=[('supervisor', 'Supervisor'), ('driver', 'Driver')], max_length=50)),
                ('phone', models.CharField(blank=True, max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('capacity', models.IntegerField()),
                ('currnt_capacity', models.IntegerField(default=0)),
                ('image', models.ImageField(default='', upload_to='main_app/static/uploads/')),
                ('description', models.TextField(max_length=250)),
                ('code', models.CharField(blank=True, db_index=True, max_length=50, unique=True)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.destination')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.source')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.transporttype')),
            ],
        ),
        migrations.AddField(
            model_name='container',
            name='transport',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main_app.transport'),
        ),
    ]
