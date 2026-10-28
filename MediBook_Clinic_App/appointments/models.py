import uuid
from django.db import models
from django.utils.text import slugify
class Specialty(models.Model):
    name=models.CharField(max_length=80,unique=True)
    slug=models.SlugField(max_length=90,unique=True,blank=True)
    def save(self,*a,**kw):
        if not self.slug:self.slug=slugify(self.name)
        super().save(*a,**kw)
    def __str__(self):return self.name
class Doctor(models.Model):
    full_name=models.CharField(max_length=120)
    specialty=models.ForeignKey(Specialty,on_delete=models.PROTECT)
    bio=models.TextField(max_length=1200)
    consultation_fee=models.DecimalField(max_digits=8,decimal_places=2)
    photo=models.ImageField(upload_to="doctors/",blank=True,null=True)
    is_accepting=models.BooleanField(default=True)
    date_created=models.DateTimeField(auto_now_add=True)
    def __str__(self):return self.full_name
class Appointment(models.Model):
    VISITS=[("In-Clinic","In-Clinic"),("Teleconsultation","Teleconsultation")]
    STATUSES=[("Pending","Pending"),("Confirmed","Confirmed"),("Cancelled","Cancelled")]
    SLOTS=[("09:00","09:00 AM"),("10:00","10:00 AM"),("11:00","11:00 AM"),("13:00","01:00 PM"),("14:00","02:00 PM"),("15:00","03:00 PM")]
    reference=models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
    doctor=models.ForeignKey(Doctor,on_delete=models.PROTECT,related_name="appointments")
    patient_name=models.CharField(max_length=120); email=models.EmailField(blank=True); phone=models.CharField(max_length=13)
    appointment_date=models.DateField(); time_slot=models.CharField(max_length=5,choices=SLOTS)
    visit_type=models.CharField(max_length=20,choices=VISITS,default="In-Clinic")
    reason=models.CharField(max_length=300); status=models.CharField(max_length=12,choices=STATUSES,default="Pending")
    date_created=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["doctor","appointment_date","time_slot"],condition=~models.Q(status="Cancelled"),name="unique_active_doctor_slot")]
