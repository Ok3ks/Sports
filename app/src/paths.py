import os

BASE_DIR = os.path.realpath(os.path.curdir)
APP_DIR = os.path.join(BASE_DIR, 'app')
REPORT_DIR = os.path.join(APP_DIR, 'reports')
WEEKLY_REPORT_DIR = os.path.join(REPORT_DIR, 'weekly_report')
FPL_WRAP_DIR = os.path.join(REPORT_DIR, 'fpl_wrap')