import random
import string
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def generate_captcha(length: int = 4) -> tuple[str, io.BytesIO]:
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '').replace('L', '')
    captcha_text = ''.join(random.choices(chars, k=length))
    
    width = 200
    height = 80
    
    bg_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    for _ in range(random.randint(3, 6)):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        line_color = (random.randint(100, 180), random.randint(100, 180), random.randint(100, 180))
        draw.line([(x1, y1), (x2, y2)], fill=line_color, width=2)
    
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        dot_color = (random.randint(100, 180), random.randint(100, 180), random.randint(100, 180))
        draw.point((x, y), fill=dot_color)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            font = ImageFont.load_default()
    
    x_start = 20
    for i, char in enumerate(captcha_text):
        char_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        
        y_offset = random.randint(-10, 10)
        
        char_img = Image.new('RGBA', (50, 70), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((5, 5), char, font=font, fill=char_color)
        
        angle = random.randint(-25, 25)
        char_img = char_img.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
        
        image.paste(char_img, (x_start + i * 45, 10 + y_offset), char_img)
    
    image = image.filter(ImageFilter.SMOOTH)
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    return captcha_text, buffer
