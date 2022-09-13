import csv

f =csv.reader(open('./gun_path/ak47.csv',encoding='utf-8'))
list =[]
for i in f:
    list.append(i)
print(list)