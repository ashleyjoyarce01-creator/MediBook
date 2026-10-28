import json
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404,redirect,render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Doctor,Specialty,Appointment
from .forms import DoctorForm,AppointmentForm
def htmx(r):return r.headers.get("HX-Request")=="true"
def doctor_list(r):
    qs=Doctor.objects.select_related("specialty").all();q=r.GET.get("q","").strip();specs=r.GET.getlist("specialty") or ([r.GET.get("specialty")] if r.GET.get("specialty") else []);extra=r.GET.get("selected_specialties", "").strip();specs=list(dict.fromkeys(specs + [v for v in extra.split(",") if v]));spec=r.GET.get("specialty","");sort=r.GET.get("sort","name")
    if q:
        from django.db.models import Q
        qs=qs.filter(Q(full_name__icontains=q)|Q(bio__icontains=q))
    if specs:qs=qs.filter(specialty__slug__in=specs)
    qs=qs.order_by({"fee_low":"consultation_fee","fee_high":"-consultation_fee","name":"full_name"}.get(sort,"full_name"))
    count=qs.count();page=max(1,int(r.GET.get("page",1)) if r.GET.get("page","1").isdigit() else 1);start=(page-1)*6
    ctx={"doctors":qs[start:start+6],"specialties":Specialty.objects.all(),"q":q,"selected_specialty":spec,"selected_specialties":specs,"sort":sort,"count":count,"page":page,"has_previous":page>1,"has_next":start+6<count,"previous_page":page-1,"next_page":page+1}
    return render(r,"appointments/partials/doctor_grid.html" if htmx(r) else "appointments/doctor_list.html",ctx)
def doctor_detail(r,pk):return render(r,"appointments/doctor_detail.html",{"doctor":get_object_or_404(Doctor.objects.select_related("specialty"),pk=pk)})
def slots(r,pk):
    doctor=get_object_or_404(Doctor,pk=pk);day=r.GET.get("appointment_date","")
    booked=list(Appointment.objects.filter(doctor=doctor,appointment_date=day).exclude(status="Cancelled").values_list("time_slot",flat=True)) if day else []
    return render(r,"appointments/partials/slot_options.html",{"slots":Appointment.SLOTS,"booked":booked,"selected":r.GET.get("time_slot", "")})
def book(r,pk):
    doctor=get_object_or_404(Doctor,pk=pk)
    if not doctor.is_accepting:
        messages.error(r,"This doctor is not accepting new patients.");return redirect("doctor_detail",pk=pk)
    form=AppointmentForm(r.POST or None,doctor=doctor)
    if r.method=="POST" and form.is_valid():
        obj=form.save(commit=False);obj.doctor=doctor
        try:obj.save()
        except IntegrityError:form.add_error("time_slot","This slot was just booked. Choose another.")
        else:
            if htmx(r):
                out=HttpResponse("");out["HX-Redirect"]=reverse("confirmation",args=[obj.pk]);out["HX-Trigger"]=json.dumps({"toast":{"message":"Appointment status updated","type":"success"},"appointment-updated":{"id":a.pk,"status":new_status}});return out
            return redirect("confirmation",pk=obj.pk)
    if r.method=="POST" and htmx(r):return render(r,"appointments/partials/booking_form.html",{"form":form,"doctor":doctor,"wizard_step":r.POST.get("wizard_step", "1")})
    return render(r,"appointments/appointment_form.html",{"form":form,"doctor":doctor,"wizard_step":r.POST.get("wizard_step", "1")})
def confirmation(r,pk):return render(r,"appointments/appointment_success.html",{"appointment":get_object_or_404(Appointment.objects.select_related("doctor","doctor__specialty"),pk=pk)})
def manage_doctors(r):
    qs=Doctor.objects.select_related("specialty");q=r.GET.get("q","")
    if q:qs=qs.filter(full_name__icontains=q)
    return render(r,"appointments/doctor_manage.html",{"doctors":qs,"q":q})
def doctor_form(r,pk=None):
    obj=get_object_or_404(Doctor,pk=pk) if pk else None;form=DoctorForm(r.POST or None,r.FILES or None,instance=obj)
    if r.method=="POST" and form.is_valid():form.save();messages.success(r,"Doctor saved successfully.");return redirect("manage_doctors")
    return render(r,"appointments/doctor_form.html",{"form":form,"heading":"Edit doctor" if obj else "Add doctor"})
@require_POST
def toggle(r,pk):
    d=get_object_or_404(Doctor,pk=pk);d.is_accepting=not d.is_accepting;d.save()
    if htmx(r):return render(r,"appointments/partials/doctor_row.html",{"doctor":d})
    return redirect("manage_doctors")
@require_POST
def delete_doctor(r,pk):
    d=get_object_or_404(Doctor,pk=pk)
    if d.appointments.exists():
        if htmx(r):
            return HttpResponse('<tr><td colspan="6">Cannot delete: doctor has appointment records.</td></tr>')
        messages.error(r,"Doctor has appointment records.")
    else:
        d.delete()
        if htmx(r): return HttpResponse("")
        messages.success(r,"Doctor deleted.")
    return redirect("manage_doctors")
def manage_appointments(r):
    appts=Appointment.objects.select_related("doctor","doctor__specialty")
    data=list(appts.values("id","patient_name","status"))
    return render(r,"appointments/appointment_manage.html",{"appointments":appts,"initial_data":data})
@require_POST
def status(r,pk,new_status):
    if new_status not in ["Confirmed","Cancelled"]:return HttpResponseBadRequest("Invalid status")
    a=get_object_or_404(Appointment,pk=pk);a.status=new_status;a.save()
    if htmx(r):
        out=HttpResponse(render_to_string("appointments/partials/appointment_row.html",{"appointment":a},request=r));out["HX-Trigger"]=json.dumps({"toast":{"message":"Appointment status updated","type":"success"},"appointment-updated":{"id":a.pk,"status":new_status}});return out
    return redirect("manage_appointments")
