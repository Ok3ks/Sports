from __future__ import annotations

bind = ":8000"
workers = 6
wsgi_app = "LiveProject.wsgi:application"
timeout = 300
max_requests = 120
threads = 4
spew = True
loglevel = 'info'

