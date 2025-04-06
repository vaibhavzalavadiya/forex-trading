# forex_backtester/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forex_backtester.settings')
application = get_wsgi_application()
