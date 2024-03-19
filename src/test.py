#!/usr/bin/python3

# Obtain an image from the camera along with the exact metadata that
# that describes that image.

import time
import numpy as np
from picamera2 import Picamera2

picam2 = Picamera2()
#picam2.start_preview(Preview.QTGL)

preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)

picam2.start()
time.sleep(2)

request = picam2.capture_request()
image = np.array(request.make_image("main"))  # image from the "main" stream
metadata = request.get_metadata()
request.release()  # requests must always be returned to libcamera
print(image)
#image.show()
print(metadata)