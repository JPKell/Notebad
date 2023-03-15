from src.langs.abl_master import ABL

abl = [x['keyword'] for x in ABL]

abl.sort(key=lambda x: len(x), reverse=True)

print(abl)