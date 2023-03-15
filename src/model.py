from models.process import lexer

class LanguageModel:
    def __init__(self):
        # The primary widget in the model is the text area to the model should know about it
        ...

    def decompose(self, txt:str) -> None:
        lexer.input(txt)
        while True:
            tok = lexer.token()
            if not tok: break
            print(tok)
    

