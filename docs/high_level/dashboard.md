# Web Dashboard Guide

## Overview

This application includes a web-based dashboard built with the Django framework. The dashboard provides a user interface to monitor the status of studies being processed by the transcription service.

It reads data directly from the MongoDB database (`studies` and `transcriptions` collections) where the core service logs its progress and results.

## Accessing the Dashboard

1.  **Ensure Prerequisites are Met:**
    *   The `google-ai` Conda environment must be active.
    *   The MongoDB server must be running and accessible.
    *   Django database migrations must have been applied (`python manage.py migrate` in the `dashboard` directory).
2.  **Start the Django Development Server:**
    Open a terminal, navigate to the `dashboard` directory within the project, and run:
    ```bash
    python manage.py runserver
    ```
3.  **Open in Browser:**
    Access the dashboard in your web browser, typically at:
    *   **Main Dashboard:** `http://127.0.0.1:8000/`
    *   **Admin Interface:** `http://127.0.0.1:8000/admin/` (Requires login using the superuser created with `python manage.py createsuperuser`).

## Features

*   **Study List View (`/`):**
    *   Displays a table of all studies known to the system (present in the MongoDB `studies` collection).
    *   Shows key information like `Study Key`, `Status`, `Received Timestamp`, `Last Updated Timestamp`.
    *   Status is color-coded for quick visual identification.
    *   Provides links to the detail view for each study.
*   **Study Detail View (`/study/<study_key>/`):**
    *   Shows detailed information for a single study from the `studies` collection.
    *   Displays associated transcriptions from the `transcriptions` collection, including the report text and timestamp.
    *   Shows error messages if the study status is `error`.
*   **Admin Interface (`/admin/`):**
    *   Provides direct access to the underlying MongoDB data as represented by the Django models (`Study`, `Transcription`).
    *   Allows viewing, searching, filtering, and potentially editing the raw data (use with caution).
    *   Useful for debugging and administration.

## Technical Details

*   **Framework:** Django
*   **Database Connection:** Uses `djongo` to connect Django models to the MongoDB database specified in `config.yaml`.
*   **Key Files:**
    *   `dashboard/manage.py`: Django command-line utility.
    *   `dashboard/dashboard/settings.py`: Project settings (database connection, installed apps, etc.).
    *   `dashboard/dashboard/urls.py`: Main URL routing.
    *   `dashboard/study_dashboard/models.py`: Defines the `Study` and `Transcription` models.
    *   `dashboard/study_dashboard/views.py`: Contains logic for rendering the list and detail pages.
    *   `dashboard/study_dashboard/urls.py`: App-specific URL routing.
    *   `dashboard/study_dashboard/templates/`: HTML templates for the user interface.
    *   `dashboard/study_dashboard/admin.py`: Configuration for the Django admin interface.

## Deployment Notes

The Django development server (`runserver`) is **not suitable for production**. For deploying the dashboard in a production environment, standard Django deployment practices should be followed, typically involving:

*   A WSGI server (like Gunicorn or uWSGI).
*   A reverse proxy (like Nginx or Apache) to handle static files and proxy requests.
*   Setting `DEBUG = False` in `settings.py`.
*   Configuring `ALLOWED_HOSTS` correctly.
*   Ensuring the production server can connect to the MongoDB database.

## Related Documents
- [System Architecture](architecture.md)
- [Installation Guide](installation.md) 