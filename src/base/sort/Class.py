def tax():
    def add(func):
        func.price = func.price * 1.2

    return add


class Phone:
    language = 'zh'

    def __init__(self, name: str, color: str, price: int):
        self.name = name
        self.color = color
        self.price = price
        if name.__contains__("iphone"):
            Phone.language = 'us'
        else:
            Phone.language = 'zh'

    def print_color(self):
        print("颜色：" + self.color)

    def print_price(self):
        print("价格：" + str(self.price))

    @classmethod
    def print_language(cls):
        print("运营商所属地区：" + cls.language)


phone = Phone('iphoneX', 'white', 6900)
# phone.print_color()
#
# Phone.print_price(Phone('HuaWei Mate30 Pro', 'black', 5699))

# print(Phone.language)
#
# Phone.print_language()
#
# phone.print_language()
