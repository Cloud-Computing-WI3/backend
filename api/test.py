#Here you go
from iteround import saferound

categories_and_pointers =  { "category_name1" : "pointer1",
                                "category_name2" : "pointer2",
                                "category_name3" : "pointer3"}
page_size = 20
# page_sizes = "category_name1" : "psize",
#                                 "category_name2" : "psize",
#                                 "category_name3" : "psize"}
# create list with float values with a corresponding total to page_size
round_list = saferound([page_size/len(categories_and_pointers) for x in categories_and_pointers], places=0)
page_sizes = {key: None for (key, value) in categories_and_pointers.items()}
# get keys as list
key_list = list(page_sizes.keys())
# match categories to values, convert to int
for i in range(0, len(round_list)):
    page_sizes[key_list[i]] = int(round_list[i])



for idx, key in enumerate(list(page_sizes.keys())):
    page_sizes[key] = round_list[idx]


print(round_list)






'''
num, div = 15, 4
print ([num // div + (1 if x < num % div else 0)  for x in range (div)])
'''