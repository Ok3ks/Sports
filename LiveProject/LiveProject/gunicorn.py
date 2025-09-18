from __future__ import annotations

import multiprocessing

bind = ":8000"
workers = multiprocessing.cpu_count() * 2 + 1
wsgi_app = "LiveProject.wsgi:application"
