import re

from models import abl
from models.modules import lex

class LanguageModel:
    def __init__(self):
        # The primary widget in the model is the text area to the model should know about it
        self.model = []

    def build_ast(self, txt:str) -> None:
        lexer = lex.lex(module=abl, reflags=re.VERBOSE | re.IGNORECASE)
        lexer.input(txt)

        self.model = []
        while True:
            tok = lexer.token()
            if not tok: break
            print(tok)
            self.model.append(tok)
        
    def capitalize_syntax(self, txt:str) -> list:
        ''' Take code as input and return code with syntax words in caps '''
        self.build_ast(txt)
        ignore = ['SNG_COMMENT', 'MULTI_COMMENT', 'SNG_STRING', 'DBL_STING', 'NUMBER', 'ID', 'CURLY_BRACE']
        output = []
        for token in self.model:
            if not token.tag: 
                token.tag = ''
            if token.type in ignore:
                value = str(token.value)
            else:    
                value = str(token.value).upper()
            
            output.append((value, f'{token.lineno}.{token.colno}', token.lineno, token.tag))
            
        return output
    

 