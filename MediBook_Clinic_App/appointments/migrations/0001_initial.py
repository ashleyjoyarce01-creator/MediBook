# Generated for MediBook clinic appointment app.
import uuid
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Specialty", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("name", models.CharField(max_length=80, unique=True)), ("slug", models.SlugField(blank=True, max_length=90, unique=True))]),
        migrations.CreateModel(name="Doctor", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("full_name", models.CharField(max_length=120)), ("bio", models.TextField(max_length=1200)), ("consultation_fee", models.DecimalField(decimal_places=2, max_digits=8)), ("photo", models.ImageField(blank=True, null=True, upload_to="doctors/")), ("is_accepting", models.BooleanField(default=True)), ("date_created", models.DateTimeField(auto_now_add=True)), ("specialty", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="appointments.specialty"))]),
        migrations.CreateModel(name="Appointment", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("reference", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)), ("patient_name", models.CharField(max_length=120)), ("email", models.EmailField(blank=True, max_length=254)), ("phone", models.CharField(max_length=13)), ("appointment_date", models.DateField()), ("time_slot", models.CharField(choices=[("09:00", "09:00 AM"), ("10:00", "10:00 AM"), ("11:00", "11:00 AM"), ("13:00", "01:00 PM"), ("14:00", "02:00 PM"), ("15:00", "03:00 PM")], max_length=5)), ("visit_type", models.CharField(choices=[("In-Clinic", "In-Clinic"), ("Teleconsultation", "Teleconsultation")], default="In-Clinic", max_length=20)), ("reason", models.CharField(max_length=300)), ("status", models.CharField(choices=[("Pending", "Pending"), ("Confirmed", "Confirmed"), ("Cancelled", "Cancelled")], default="Pending", max_length=12)), ("date_created", models.DateTimeField(auto_now_add=True)), ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="appointments", to="appointments.doctor"))]),
        migrations.AddConstraint(model_name="appointment", constraint=models.UniqueConstraint(condition=models.Q(status="Cancelled", _negated=True), fields=("doctor", "appointment_date", "time_slot"), name="unique_active_doctor_slot")),
    ]
