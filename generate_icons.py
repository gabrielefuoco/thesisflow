from PIL import Image, ImageDraw

def create_icon(name, draw_func, size=(48, 48), color="#cbd5e1"):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_func(draw, size, color)
    img.save(f"assets/icons/{name}.png")

def draw_project(d, s, c):
    w, h = s
    d.rectangle((4, 8, w-4, h-8), outline=c, width=3)
    d.rectangle((4, 8, 16, 12), fill=c) # Tab

def draw_plus(d, s, c):
    w, h = s
    m = 12
    d.line((w/2, m, w/2, h-m), fill=c, width=4)
    d.line((m, h/2, w-m, h/2), fill=c, width=4)

def draw_trash(d, s, c):
    w, h = s
    d.rectangle((14, 16, w-14, h-8), outline=c, width=3)
    d.line((10, 12, w-10, 12), fill=c, width=3) # Lid
    d.line((w/2-5, 20, w/2-5, h-12), fill=c, width=2)
    d.line((w/2+5, 20, w/2+5, h-12), fill=c, width=2)

def draw_settings(d, s, c):
    w, h = s
    d.ellipse((8, 8, w-8, h-8), outline=c, width=3)
    d.ellipse((w/2-6, h/2-6, w/2+6, h/2+6), outline=c, width=3)

def draw_chevron_right(d, s, c):
    w, h = s
    points = [(16, 12), (32, h/2), (16, h-12)]
    d.line(points, fill=c, width=4)

def draw_chevron_down(d, s, c):
    w, h = s
    points = [(12, 16), (w/2, 32), (w-12, 16)]
    d.line(points, fill=c, width=4)

def draw_bold(d, s, c):
    w, h = s
    font_size = 32
    # Simple representation without font
    d.text((12, 6), "B", fill=c, font_size=32)

def draw_italic(d, s, c):
    d.text((16, 6), "I", fill=c, font_size=32)

def draw_list(d, s, c):
    w, h = s
    for i in range(3):
        y = 12 + i*12
        d.ellipse((8, y, 12, y+4), fill=c)
        d.line((18, y+2, w-8, y+2), fill=c, width=3)

def draw_play(d, s, c):
    w, h = s
    d.polygon([(14, 10), (14, h-10), (w-10, h/2)], fill=c)

def draw_image(d, s, c):
    w, h = s
    d.rectangle((6, 10, w-6, h-10), outline=c, width=3)
    d.ellipse((w/2, 16, w/2+6, 22), fill=c)
    d.polygon([(6, h-10), (16, h/2), (26, h-10)], fill=c)

def draw_folder(d, s, c):
    w, h = s
    d.polygon([(4, 8), (20, 8), (24, 14), (w-4, 14), (w-4, h-8), (4, h-8)], fill=c)

def draw_file(d, s, c):
    w, h = s
    d.polygon([(10, 6), (w-16, 6), (w-10, 14), (w-10, h-6), (10, h-6)], outline=c, width=3)
    d.line((14, 14, w-14, 14), fill=c, width=2)
    d.line((14, 22, w-14, 22), fill=c, width=2)

def draw_edit(d, s, c):
    w, h = s
    d.line((w-12, 8, 8, h-12), fill=c, width=3)
    d.polygon([(8, h-12), (14, h-12), (8, h-6)], fill=c)

if __name__ == "__main__":
    create_icon("project", draw_project)
    create_icon("plus", draw_plus)
    create_icon("trash", draw_trash)
    create_icon("settings", draw_settings)
    create_icon("chevron_right", draw_chevron_right)
    create_icon("chevron_down", draw_chevron_down)
    create_icon("bold", draw_bold)
    create_icon("italic", draw_italic)
    create_icon("list", draw_list)
    create_icon("play", draw_play, color="#0ea5e9") # Accent
    create_icon("image", draw_image)
    create_icon("folder", draw_folder)
    create_icon("file", draw_file)
    create_icon("edit", draw_edit)
    create_icon("close", draw_plus) # Rotate in code or just use + for now
    
    # Missing ones
    create_icon("quote", draw_bold) # Reuse bold style or text
    create_icon("down", draw_chevron_down)
    create_icon("up", draw_chevron_right) # Wrong direction but placeholder
    create_icon("list", draw_list)
