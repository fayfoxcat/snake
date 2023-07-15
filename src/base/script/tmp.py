def my_function(a, list=[]):
    list.append(a)
    return list


var1 = my_function(10)
var2 = my_function(3, [])
var3 = my_function('abc')

print(var1)
print(var2)
print(var3)
