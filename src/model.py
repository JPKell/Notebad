import re

from models import abl2
from models.modules import lex
# from models.abl_rules import build

class LanguageModel:
    def __init__(self):
        # The primary widget in the model is the text area to the model should know about it
        self.model = []

        self.expand = False

    def build_ast(self, txt:str) -> None:
        lexer = lex.lex(module=abl2, reflags=re.VERBOSE | re.IGNORECASE)
        lexer.input(txt)
        self.model = []

        while True:
            try:
                tok = lexer.token()
            except Exception as e:
                tok = None
                print(e)
    
            if not tok: break
            self.model.append(tok)
        
    def get_syntax_token(self, txt:str) -> str:
        ''' Get the syntax tag for a given word '''
        self.build_ast(txt)
        return [ tok for tok in self.model if tok.type != 'newline' ]


    def format_syntax(self, txt:str, no_nl=False, expand=True, upper=True) -> list:
        ''' Take code as input and return code with syntax words in caps '''
        self.build_ast(txt)
        ignore = ['SNG_COMMENT', 'MULTI_COMMENT', 'SNG_STRING', 'DBL_STRING', 'NUMBER', 'ID', 'ERROR', 'CURLY_BRACE']
        output = []
        for token in self.model:
            # Not sure if the no_nl is still needed
            if no_nl and token.tag == 'nl':
                continue
            if not token.tag: 
                token.tag = ''
            if token.type not in ignore and upper:
                token.value = str(token.value).upper()

            if expand:
                self.expand_syntax(token)

            output.append(token)
            
        return output
    

    def expand_syntax(self, token):
        if token.value in token.type:
            token.value = token.type.replace('_', '-')
