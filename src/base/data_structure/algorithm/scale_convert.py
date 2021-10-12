def scale_convert(value, base):
    convert = "0123456789ABCDEF"
    if value < base:
        return convert[value]
    else:
        return scale_convert(value // base, base) + convert[value % base]


print(scale_convert(12306, 16))
