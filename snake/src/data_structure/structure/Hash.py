def hash(astring, tablesize):
    sum = 0
    for pos in range(len(astring)):
        sum = sum + ord(astring[pos]) * (pos + 1)
    return sum % tablesize


string = 'bool'
table = 10
result = hash(string, table)
print(result)
