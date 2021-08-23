# def question():
#     print("/n")
#     name = input("今天天气怎么样？")
#     print("今天天气", name)
#
#
# '''
# question()
# '''
#
list = [1, 2, 3, 4]
#
# list.append(5)
# print(list)
# list.insert(0,0)
# print(list)
#
# print(list[-1])
# # list.sort(key=lambda i:i,reverse=True)
# print(list)
# list.remove(3)
#
# print(list)
# copy = list.copy()
#
# print(copy)
#
map = [{"id": 12, "name": "徐凤年", 'age': "18"}]
fruits = ['apple', 'banana', 'cherry']
fruits.extend(map)

# print(fruits)


newMap = fruits[-1].copy()
# print(newMap.get('name'))
# print(newMap['name'])

print(newMap)

# newMap.pop('name')

keys = newMap.keys()
print(keys)

print(newMap.values())

newDict = {}

fromkeys = newDict.fromkeys(newMap,None)

print(fromkeys)

print('------------------------------------------------------')
map = {"id": 12, "name": "徐凤年", 'age': "18"}

testMap = {'url': 'https://www.baidu.com'}

# map.popitem()
map.pop(u'key')
# map.append({'url': 'https://www.baidu.com'})

print(map)
