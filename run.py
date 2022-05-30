import board
import adafruit_ssd1306
import digitalio
from PIL import Image, ImageDraw, ImageFont
import time

BORDER = 5
BAR = 2

units = {
    "liter": ["mL", "L", "kL"],
    "gram": ["mg", "g", "kg"]
}

def init_display():
    oled_reset = digitalio.DigitalInOut(board.D4)
    i2c = board.I2C()
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, #addr=0x3d, 
                                        reset=oled_reset)
    clear(oled)
    return oled

def clear(oled):
    # Clear display.
    oled.fill(0)
    oled.show()

def draw(oled, current, target, unit):
    if unit not in units:
        raise Exception("Unsupported unit used")
    
    if current > target:
        raise Exception("Current bigger than target")

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new("1", (oled.width, oled.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a white background
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

    # Draw a smaller inner rectangle
    draw.rectangle(
        (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
        outline=0,
        fill=0,
    )
    
    #draw progress rectangle
    progress = current/target
    if progress > 0.01:
        draw.rectangle(
            (BORDER+BAR, BORDER+BAR, max(oled.width * progress - BORDER - 1 - BAR, BORDER+BAR), oled.height - BORDER - 1 - BAR),
            outline=255,
            fill=255
        )

    # Load default font.
    font = ImageFont.load_default()

    # Draw Some Text
    val = current
    idx = 0
    while val >= 1000 and idx < 2:
        val = val/1000
        idx += 1
    text = f"{val}{units[unit][idx]}"
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )

    # Display image
    oled.image(image)
    oled.show()
    
oled = init_display()
try:
    current = 0
    target = 1000
    while True:
        print(f"{current}/{target}")
        draw(oled, current, target, "gram")
        time.sleep(0.1)
        current += target / 10
        if current > target:
            current = 0
except KeyboardInterrupt:
    print("Shutting down.")
    clear(oled)