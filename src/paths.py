import os

BASE_DIR = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))  # make this absolute
SRC_DIR = os.path.join(BASE_DIR, "src")
APP_DIR = os.path.join(BASE_DIR, "app")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
FPL_WRAP_DIR = os.path.join(REPORT_DIR, "fpl_wrap")
WEEKLY_REPORT_DIR = os.path.join(REPORT_DIR, "weekly_report")
MISC_DIR = os.path.join(BASE_DIR, "misc")
MOCK_DIR = os.path.join(MISC_DIR, "mock_data")

if __name__ == "__main__":
    print(
        """ BASE_DIR:{}\n 
            SRC_DIR{}\n
            APP_DIR{}\n
            REPORT_DIR{}\n
            FPL_WRAP_DIR{}\n
            MISC_DIR{} \n
            WEEKLY_REPORT_DIR{}
        """.format(
            BASE_DIR, SRC_DIR, APP_DIR, REPORT_DIR, FPL_WRAP_DIR, MISC_DIR, WEEKLY_REPORT_DIR
            ))
