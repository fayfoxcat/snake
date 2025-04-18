import math

colors = {
    "BLACK1": (0, 0, 0),
    "WHITE1": (255, 255, 255),
    "RED1": (255, 0, 0),
    "BRIGHT_GREEN1": (0, 255, 0),
    "BLUE1": (0, 0, 255),
    "YELLOW1": (255, 255, 0),
    "PINK1": (255, 192, 203),
    "TURQUOISE1": (64, 224, 208),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "RED": (255, 0, 0),
    "BRIGHT_GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "PINK": (255, 192, 203),
    "TURQUOISE": (64, 224, 208),
    "DARK_RED": (139, 0, 0),
    "GREEN": (0, 128, 0),
    "DARK_BLUE": (0, 0, 139),
    "DARK_YELLOW": (204, 204, 0),
    "VIOLET": (238, 130, 238),
    "TEAL": (0, 128, 128),
    "GREY_25_PERCENT": (192, 192, 192),
    "GREY_50_PERCENT": (128, 128, 128),
    "CORNFLOWER_BLUE": (100, 149, 237),
    "MAROON": (128, 0, 0),
    "LEMON_CHIFFON": (255, 250, 205),
    "LIGHT_TURQUOISE1": (175, 238, 238),
    "ORCHID": (218, 112, 214),
    "CORAL": (255, 127, 80),
    "ROYAL_BLUE": (65, 105, 225),
    "LIGHT_CORNFLOWER_BLUE": (173, 216, 230),
    "SKY_BLUE": (135, 206, 235),
    "LIGHT_TURQUOISE": (175, 238, 238),
    "LIGHT_GREEN": (144, 238, 144),
    "LIGHT_YELLOW": (255, 255, 224),
    "PALE_BLUE": (175, 238, 238),
    "ROSE": (255, 228, 225),
    "LAVENDER": (230, 230, 250),
    "TAN": (210, 180, 140),
    "LIGHT_BLUE": (173, 216, 230),
    "AQUA": (0, 255, 255),
    "LIME": (0, 255, 0),
    "GOLD": (255, 215, 0),
    "LIGHT_ORANGE": (255, 200, 0),
    "ORANGE": (255, 165, 0),
    "BLUE_GREY": (102, 153, 204),
    "GREY_40_PERCENT": (153, 153, 153),
    "DARK_TEAL": (0, 128, 128),
    "SEA_GREEN": (46, 139, 87),
    "DARK_GREEN": (0, 100, 0),
    "OLIVE_GREEN": (128, 128, 0),
    "BROWN": (165, 42, 42),
    "PLUM": (221, 160, 221),
    "INDIGO": (75, 0, 130),
    "GREY_80_PERCENT": (51, 51, 51),
    "AUTOMATIC": (0, 0, 0)
}

def euclidean_distance(rgb1, rgb2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

def find_closest_color(target_rgb):
    closest_color = None
    min_distance = float('inf')
    for color_name, color_rgb in colors.items():
        distance = euclidean_distance(target_rgb, color_rgb)
        if distance < min_distance:
            min_distance = distance
            closest_color = color_name
    return closest_color

# 给定的颜色
color1 = (167, 216, 134)
color2 = (255, 99, 71)

closest_color1 = find_closest_color(color1)
closest_color2 = find_closest_color(color2)

print(f"The closest color to {color1} is {closest_color1}.")
print(f"The closest color to {color2} is {closest_color2}.")
