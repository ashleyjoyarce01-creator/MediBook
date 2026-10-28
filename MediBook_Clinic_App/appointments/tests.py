from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from .models import Specialty, Doctor, Appointment

class AppointmentValidationTests(TestCase):
    def setUp(self):
        self.specialty = Specialty.objects.create(name="Family Medicine")
        self.doctor = Doctor.objects.create(full_name="Dr. Test Example", specialty=self.specialty, bio="A sample doctor biography for automated testing.", consultation_fee="500.00", is_accepting=True)
        self.client = Client()
        self.future_weekday = date.today() + timedelta(days=1)
        while self.future_weekday.weekday() == 6:
            self.future_weekday += timedelta(days=1)

    def payload(self, **overrides):
        data = {"patient_name":"Jamie Example", "email":"jamie@example.com", "phone":"09123456789", "appointment_date":self.future_weekday.isoformat(), "time_slot":"10:00", "visit_type":"In-Clinic", "reason":"Routine health consultation"}
        data.update(overrides)
        return data

    def test_valid_booking_redirects_to_confirmation(self):
        response = self.client.post(reverse("book", args=[self.doctor.pk]), self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Appointment.objects.count(), 1)
        confirmation = self.client.get(response["Location"])
        self.assertEqual(confirmation.status_code, 200)
        self.assertContains(confirmation, "Jamie Example")

    def test_invalid_phone_is_rejected(self):
        response = self.client.post(reverse("book", args=[self.doctor.pk]), self.payload(phone="123"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)
        self.assertContains(response, "Enter 09XXXXXXXXX or +639XXXXXXXXX")

    def test_teleconsultation_requires_email(self):
        response = self.client.post(reverse("book", args=[self.doctor.pk]), self.payload(email="", visit_type="Teleconsultation"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)
        self.assertContains(response, "Email is required for teleconsultation")

    def test_reason_must_be_at_least_ten_characters(self):
        response = self.client.post(reverse("book", args=[self.doctor.pk]), self.payload(reason="too short"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_past_date_is_rejected(self):
        response = self.client.post(reverse("book", args=[self.doctor.pk]), self.payload(appointment_date=(date.today()-timedelta(days=1)).isoformat()))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_sunday_is_rejected(self):
        sunday = date.today() + timedelta(days=1)
        while sunday.weekday() != 6: sunday += timedelta(days=1)
        response = self.client.post(reverse("book", args=[self.doctor.pk]), self.payload(appointment_date=sunday.isoformat()))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_duplicate_doctor_date_slot_is_rejected(self):
        Appointment.objects.create(doctor=self.doctor, **self.payload())
        response = self.client.post(reverse("book", args=[self.doctor.pk]), self.payload())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_closed_doctor_cannot_be_booked_directly(self):
        self.doctor.is_accepting = False
        self.doctor.save()
        response = self.client.post(reverse("book", args=[self.doctor.pk]), self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_slot_endpoint_disables_booked_slots(self):
        Appointment.objects.create(doctor=self.doctor, **self.payload())
        response = self.client.get(reverse("slots", args=[self.doctor.pk]), {"appointment_date":self.future_weekday.isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Booked")

    def test_htmx_directory_returns_partial(self):
        response = self.client.get(reverse("doctor_list"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/partials/doctor_grid.html")

    def test_specialty_filter_returns_matching_doctors(self):
        other = Specialty.objects.create(name="Pediatrics")
        Doctor.objects.create(full_name="Dr. Pediatric Test", specialty=other, bio="Pediatric care for children and families.", consultation_fee="600.00")
        response = self.client.get(reverse("doctor_list"), {"specialty": [self.specialty.slug]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Test Example")
        self.assertNotContains(response, "Dr. Pediatric Test")

    def test_htmx_validation_swaps_partial_and_preserves_value(self):
        response = self.client.post(reverse("book", args=[self.doctor.pk]), self.payload(phone="123", wizard_step="1"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/partials/booking_form.html")
        self.assertContains(response, 'value="123"')
        self.assertContains(response, "Enter 09XXXXXXXXX or +639XXXXXXXXX")

    def test_doctor_form_rejects_zero_consultation_fee(self):
        response = self.client.post(reverse("doctor_add"), {"full_name":"Dr. Invalid Fee", "specialty":self.specialty.pk, "bio":"This is a sample biography.", "consultation_fee":"0", "is_accepting":"on"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Doctor.objects.filter(full_name="Dr. Invalid Fee").exists())
        self.assertContains(response, "Consultation fee must be greater than 0")
