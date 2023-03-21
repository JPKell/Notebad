from ._keywords import keyword_master as kw

def print_category_counts() -> None:
    ''' Print the number of keywords in each category. Good for while tweaking'''
    cats = set([x['cat'] for x in kw])
    key_cats = { x:0 for x in list(cats) }
    for k in kw:
        key_cats[k['cat']] += 1
    for k in key_cats:
        print(k, key_cats[k])



