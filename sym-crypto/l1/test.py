with open('C:\\Users\\dimas\\Desktop\\java\\lab1_resources\\TEXT', 'r') as file:
	data = file.read()
print(data.decode('cp-1251').encode('utf-8'))