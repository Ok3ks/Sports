import os

BASE_DIR = os.path.realpath(os.path.dirname(os.path.dirname(__file__))) #make this absolute
SRC_DIR = os.path.join(BASE_DIR, 'src')
APP_DIR = os.path.join(BASE_DIR, 'app')
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
FPL_WRAP_DIR = os.path.join(REPORT_DIR, 'fpl_wrap')
WEEKLY_REPORT_DIR = os.path.join(REPORT_DIR, 'weekly_report')

if __name__ == "__main__":
    print("{}\n{}\n{}\n{}\n{}".format(BASE_DIR,SRC_DIR, APP_DIR, REPORT_DIR, WEEKLY_REPORT_DIR))