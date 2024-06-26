# -*- coding: utf-8 -*-

import os.path

here = os.path.abspath(os.path.dirname(__file__))
base = os.path.abspath(os.path.join(here, ".."))

DEBUG_TB_INTERCEPT_REDIRECTS = False

DEBUG = True
SECRET_KEY = "AAAAB3NzaC1yc2EAAAADAQABAAABAQD3N7z5Ir+tRxRmJD+IO+CUG2kte/ISDVRiUUrMGIQTEv+drgXutJ8tKd06Th+oDWE7kGhV+8i0NIaHz1w9wkdRr1CNpVA5r5xXYgPSrcurUVR7GFvTtgwmXjHRXAfHm7ENcrZLs0VP2sE34KSMOdXu+uiDovZCIeOPwFpO/7gAoiXLhVIowwOR9jUH/whLW0/DGXHajf0bO0uxPt/7jbHsahrCf2/h82V/QKWj+HEfsa38Z6V3vxNqYMtMUuDiaS1SeLdmWkL49sDOTpoBiAnrYJihK06MNb2+UZCsEliHKccCXSm/386yGyadHp1iXXpBmxqkM476kqC99uBwvzpP"

SMTP_SERVER = "localhost"
EMAIL_FROM = "SkyLines <no-reply@skylinescondor.com>"

"""
# Logging handlers (disabled in DEBUG mode)

file_handler = (
    'INFO', 'RotatingFileHandler',
    ('/home/turbo/skylines.log', 'a', 10000, 4))

LOGGING_HANDLERS = [file_handler]

SENTRY_DSN = 'https://foo:bar@sentry.io/appid'
"""

# This should probably be changed for a multi-threaded production server
CACHE_TYPE = "simple"

SQLALCHEMY_DATABASE_URI = "postgresql:///skylines"
SQLALCHEMY_TRACK_MODIFICATIONS = False

ASSETS_LOAD_DIR = os.path.join(base, "skylines", "frontend", "static")

SKYLINES_FILES_PATH = os.path.join(base, "htdocs", "files")
SKYLINES_ELEVATION_PATH = os.path.join(base, "htdocs", "srtm")
SKYLINES_MAPSERVER_PATH = os.path.join(base, "mapserver")

SKYLINES_TEMPORARY_DIR = "/tmp"

# how many entries should a list have?
SKYLINES_LISTS_DISPLAY_LENGTH = 50

SKYLINES_MAP_TILE_URL = "https://skylinescondor.com/mapproxy"

BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERYD_LOG_LEVEL = "INFO"

# limits for AnalyseFlight
SKYLINES_ANALYSIS_ITER = 10e6  # iteration limit, should be around 10e6 to 50e6
SKYLINES_ANALYSIS_MEMORY = 256  # approx memory limit in MB

# List of airspace types to check for infringements
SKYLINES_AIRSPACE_CHECK = (
    "RESTRICT",
    "DANGER",
    "PROHIBITED",
    "CTR",
    "CLASSA",
    "CLASSB",
    "CLASSC",
    "CLASSD",
    "NOGLIDER",
    "TMZ",
    "MATZ",
)
