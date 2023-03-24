import re

from language import abl
from language.modules import lex
# from models.abl_rules import build

from modules.logging import Log

logger = Log(__name__)

languages = {
    'abl': abl
}

class LanguageModel:
    def __init__(self):
        # The primary widget in the model is the text area to the model should know about it
        self.model = []
        self.language_module = None
        self.expand = False
        self.track_whitepace = False
        logger.debug('LanguageModel initialized')

    def load_language(self, lang:str) -> None:
        ''' Loads a language into the model '''

        self.language_module = languages.get(lang, None)

        if not self.language_module:
            logger.info(f'Language {lang} not found')
            return
        
        self.track_whitepace = self.language_module.track_whitespace
        logger.info(f'Language {lang} loaded')


    def build_ast(self, txt:str) -> None:
        lexer = lex.lex(module=self.language_module, reflags=re.VERBOSE | re.IGNORECASE)
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


    def format_syntax(self, txt:str, no_nl=False, expand=False, upper=False) -> list:
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
