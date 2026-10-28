# MediBook verification report

Date: 2026-10-28

## Checks completed
- Python syntax compilation: PASS (`python -m compileall -q .`)
- JavaScript syntax: PASS (`node --check appointments/static/appointments/js/app.js`)
- Sample fixture JSON parse: PASS (9 fictional doctor records)

## Blocked checks
- Django system checks and Django tests: NOT RUN. Django is not installed in the execution environment. `pip install -r requirements.txt` failed because the package index could not be resolved (network/DNS unavailable).
- Browser UI/HTMX/Alpine tests: NOT RUN because the Django server could not be started.
- Genuine runtime screenshots: NOT CAPTURED. The Word document marks the required evidence as pending instead of using fabricated images.
- Public GitHub publication: PENDING GitHub connection/authorization.

## Before submission
1. Install requirements on a computer with internet access.
2. Run `python manage.py migrate`, `python manage.py loaddata appointments/fixtures/sample_data.json`, and `python manage.py test appointments`.
3. Start the server and complete all interactions in the evidence checklist in the Word document.
4. Capture actual browser screenshots at desktop, tablet, and 360px mobile widths.
5. Publish the project to a public GitHub repository and replace the pending URL.
6. Fill in the student's section in the Word document.
