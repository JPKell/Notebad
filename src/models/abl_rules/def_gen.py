''' This is used to loop over the word list i have in the abl_master file and build functions for the lexer'''

# from abl_master import ABL

# kw_dict = {}

# for kw in ABL:
#     if kw['reserved'] == False and kw['min_abr'] == None:
#         py_friendly = kw['keyword'].replace('-', '_')
#         kw_dict[kw['keyword']] = py_friendly
#         kw_tuple = (kw['keyword'], kw['min_abr'])

# #         print(f'''
# # @TOKEN(build_regex('{kw['keyword']}', '{kw['min_abr']}'))
# # def t_{py_friendly}(t):
# #     return t''')


# print(kw_dict)



import re

text = "Examples: 'F12', \"f5\", F99, f2"

pattern = r"""['"]?[fF]\d{1,2}['"]?"""
results = re.findall(pattern, text)

if results:
    for result in results:
        print(result)
else:
    print("No match found")