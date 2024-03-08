import RPi.GPIO as GPIO

pin_shutter         = 23    # shutter timing picup 
pin_led_red         = 24
pin_led_green       = 25
pin_shutdown        = 8
pin_dip1            = 7
pin_dip2            = 1
pin_dip3            = 12
pin_dip4            = 16
pin_dip5            = 20
pin_dip6            = 21

# GPIO設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_shutter,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_shutdown,    GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip1,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip2,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip3,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip4,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip5,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip6,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_led_red,     GPIO.OUT)
GPIO.setup(pin_led_green,   GPIO.OUT)

print("pin_dip1 :",GPIO.input(pin_dip1))
print("pin_dip2 :",GPIO.input(pin_dip2))
print("pin_dip3 :",GPIO.input(pin_dip3))
print("pin_dip4 :",GPIO.input(pin_dip4))
print("pin_dip5 :",GPIO.input(pin_dip5))
print("pin_dip6 :",GPIO.input(pin_dip6))
print("shutter  :",GPIO.input(pin_shutter))
print("shutdown :",GPIO.input(pin_shutdown))


while True:
    if GPIO.input(pin_shutter) == False:
        GPIO.output(pin_led_green, True)
    else:
        GPIO.output(pin_led_green, False)
    if GPIO.input(pin_shutdown) == False:
        GPIO.output(pin_led_red, True)
    else:
        GPIO.output(pin_led_red, False)
