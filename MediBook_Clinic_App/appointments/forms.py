import re
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Doctor,Appointment
class DoctorForm(forms.ModelForm):
    class Meta:
        model=Doctor; fields=["full_name","specialty","bio","consultation_fee","photo","is_accepting"]
        labels={"full_name":"Doctor name","consultation_fee":"Consultation fee (PHP)","is_accepting":"Accepting new patients"}
        help_texts={"bio":"Short introduction, up to 1,200 characters.","consultation_fee":"Must be greater than zero."}
        widgets={"full_name":forms.TextInput(attrs={"class":"field"}),"specialty":forms.Select(attrs={"class":"field"}),"bio":forms.Textarea(attrs={"class":"field","rows":3}),"consultation_fee":forms.NumberInput(attrs={"class":"field","min":"0.01","step":"0.01"}),"photo":forms.ClearableFileInput(attrs={"class":"field"})}
    def clean_consultation_fee(self):
        v=self.cleaned_data["consultation_fee"]
        if v<=0:raise ValidationError("Consultation fee must be greater than 0.")
        return v
class AppointmentForm(forms.ModelForm):
    class Meta:
        model=Appointment; fields=["patient_name","email","phone","appointment_date","time_slot","visit_type","reason"]
        labels={"patient_name":"Patient name","email":"Email address","phone":"Mobile number","appointment_date":"Appointment date","time_slot":"Available time","visit_type":"Visit type","reason":"Reason for visit"}
        help_texts={"phone":"Use 09XXXXXXXXX or +639XXXXXXXXX.","reason":"At least 10 characters; maximum 300."}
        widgets={"patient_name":forms.TextInput(attrs={"class":"field","x-model":"patientName"}),"email":forms.EmailInput(attrs={"class":"field","x-model":"email"}),"phone":forms.TextInput(attrs={"class":"field","placeholder":"09XXXXXXXXX","x-model":"phone"}),"appointment_date":forms.DateInput(attrs={"class":"field","type":"date","x-model":"date"}),"time_slot":forms.Select(attrs={"class":"field","x-model":"selectedSlot"}),"visit_type":forms.Select(attrs={"class":"field","x-model":"visitType"}),"reason":forms.Textarea(attrs={"class":"field","rows":4,"maxlength":"300","x-model":"reason"})}
    def __init__(self,*a,doctor=None,**kw):
        self.doctor=doctor;super().__init__(*a,**kw)
    def clean_phone(self):
        v=self.cleaned_data["phone"].strip().replace(" ","").replace("-","")
        if not (re.fullmatch(r"09\d{9}",v) or re.fullmatch(r"\+639\d{9}",v)):raise ValidationError("Enter 09XXXXXXXXX or +639XXXXXXXXX.")
        return v
    def clean_appointment_date(self):
        v=self.cleaned_data["appointment_date"]
        if v<date.today():raise ValidationError("Appointment date cannot be in the past.")
        if v.weekday()==6:raise ValidationError("The clinic is closed on Sundays.")
        return v
    def clean(self):
        d=super().clean()
        if d.get("visit_type")=="Teleconsultation" and not d.get("email"):self.add_error("email","Email is required for teleconsultation.")
        if d.get("reason") and len(d["reason"].strip())<10:self.add_error("reason","Enter at least 10 characters.")
        if self.doctor and d.get("appointment_date") and d.get("time_slot"):
            if not self.doctor.is_accepting:raise ValidationError("This doctor is not accepting new patients.")
            qs=Appointment.objects.filter(doctor=self.doctor,appointment_date=d["appointment_date"],time_slot=d["time_slot"]).exclude(status="Cancelled")
            if self.instance.pk:qs=qs.exclude(pk=self.instance.pk)
            if qs.exists():self.add_error("time_slot","This slot is already booked.")
        return d
