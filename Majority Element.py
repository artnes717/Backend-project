list = input("List: ").split()
list = [int(i) for i in list]

result, resultIndex = 0, 0

for i in range(len(list)):
    if list.count(list[i]) > resultIndex:
        result = list[i]
        resultIndex = list.count(result)

print("The result is:", result)