# RAM usage optimization:
import gc
gc.collect()
gc.threshold(4096)
import microdot, microdot_asyncio, microdot_cors
gc.collect()
import urequests_asyncio
gc.collect()
import dfplayer
gc.collect()

import os # for pymakr upload

from network import WLAN, AP_IF
WLAN(AP_IF).active(False)
gc.collect()
