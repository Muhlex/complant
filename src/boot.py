import os # for pymakr upload
import microdot, microdot_asyncio # RAM usage optimization

from network import WLAN, AP_IF
WLAN(AP_IF).active(False)
