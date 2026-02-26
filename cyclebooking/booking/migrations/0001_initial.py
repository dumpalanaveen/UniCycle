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
            name='Cycle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('cycle_id', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='cycles/')),
                ('gear_type', models.CharField(default='Single Speed', max_length=50)),
                ('color', models.CharField(max_length=50)),
                ('condition', models.CharField(default='Good', max_length=50)),
                ('status', models.CharField(choices=[('available', 'Available'), ('booked', 'Booked'), ('maintenance', 'Under Maintenance')], default='available', max_length=20)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('roll_number', models.CharField(blank=True, max_length=20)),
                ('department', models.CharField(blank=True, max_length=100)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_date', models.DateTimeField(auto_now_add=True)),
                ('duration_minutes', models.PositiveIntegerField()),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('status', models.CharField(choices=[('pending_payment', 'Pending Payment'), ('confirmed', 'Confirmed'), ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending_payment', max_length=20)),
                ('unlock_pin', models.CharField(blank=True, max_length=4)),
                ('payment_reference', models.CharField(blank=True, max_length=50)),
                ('qr_data', models.TextField(blank=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('returned_at', models.DateTimeField(blank=True, null=True)),
                ('actual_duration_minutes', models.PositiveIntegerField(blank=True, null=True)),
                ('refund_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('cycle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.cycle')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
