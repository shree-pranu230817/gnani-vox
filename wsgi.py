"""
WSGI Production Entry Point for Uzhavar AI.
Compatible with Gunicorn, Waitress, uWSGI, and Cloud Platforms.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
