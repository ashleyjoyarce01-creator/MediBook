# MediBook Clinic Appointments — IT 424 Test III and IV

## Setup (Windows)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata appointments/fixtures/sample_data.json
python manage.py runserver
```
Open http://127.0.0.1:8000/. Staff pages: `/manage/doctors/` and `/manage/appointments/`. Use `python manage.py createsuperuser` for optional Django admin access.

## Automated tests
Run `python manage.py test appointments` to exercise valid booking, phone/date/teleconsultation/reason validation, duplicate-slot rejection, closed-doctor protection, slot rendering, HTMX partial responses, and specialty filtering.

## CDN decisions
HTMX 2.0.4 is loaded from a pinned unpkg URL in `base.html`; Alpine.js and its Persist plugin are loaded with `defer` from jsDelivr. This keeps the exam project build-free. Download and serve pinned libraries locally if offline use is required.

## HTMX and Alpine integration points
1. Directory search/filter/sort requests server-rendered HTML with `hx-get`, a 300ms debounce, and `hx-target="#doctor-grid"`.
2. Date selection requests the slot partial; Django checks bookings and disables occupied slots.
3. Booking uses `hx-post`; Django validates the form and returns swapped errors or `HX-Redirect`.
4. Staff row updates use HTMX and CSRF tokens; an `HX-Trigger` event is sent for Alpine toast feedback.
5. Alpine owns only temporary UI state (menu, tabs, wizard step, theme, toast messages). Django owns all persistent doctor and appointment data.

## Alpine component inventory
| Component | Page | State/getters | Directives/events | Scope |
|---|---|---|---|---|
| Navbar | All | open | x-data, @click, :class, @keydown.escape.window | local |
| Theme | All | dark, toggle() | @click, x-text | shared store; localStorage |
| Toast stack | All | items, add/remove | x-for :key, x-transition | shared store |
| Directory | / | search, view | x-model, x-ref, x-show, $watch, keydown | local; view persisted |
| Doctor card | / | quick | @mouseenter, @mouseleave, x-show, x-transition | per-card local |
| Detail tabs | detail | tab | x-show, :aria-selected, @click | local |
| Booking wizard | booking | step, reason, date, selectedSlot; canAdvance, remaining | x-model, x-show, :disabled, $watch, $nextTick | local |
| Appointment manager | staff appointments | active, selected; filteredItems, count | x-for, x-model, x-show, :key | local UI state |

## State map
Local `x-data` contains transient UI states such as the menu, selected tab, wizard step, and quick view. Shared stores are used for theme and toast notifications. Theme preference persists through localStorage. Doctors, specialties, appointment records, slot conflicts, and validation remain in Django/SQLite and are never stored in Alpine.

## Sample photos
The fixture includes fictional doctor records and abstract sample portrait images under `media/doctors/` so the photo display can be demonstrated without using real patient or doctor photos.

## Before submitting
The exam requires genuine screenshots and a public GitHub repository. Do not claim that a screenshot is real unless it was captured from the running Django app. Capture the actual running app at mobile (360px), tablet, and desktop sizes; show empty states, invalid forms, slot availability, booking confirmation, staff updates, Alpine interactions, and theme persistence. Add your repository link and name/section to the accompanying Word document. Staff pages are open to match the exam handout; do not deploy publicly without authentication.
