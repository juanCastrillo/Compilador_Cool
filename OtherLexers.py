from sly import Lexer
import Lexer as L

'''
Multiline comment lexer analyzer
(* *)
'''
class Comment_Ml(Lexer):
    tokens = {}
    _word = ""

    @_(r'\*\)')
    def STR_CONST(self, t):
        t.value = self._word
        self.begin(L.CoolLexer)
        self._word = ""
        return t

    @_(r'.|\n')
    def CONTENT(self, t):
        pass # self._word += t.value

    def error(self, t):
        self.index += 1 # Avanza al siguiente caracter


'''
Single line comment 
--
'''
class Comment(Lexer):
    tokens = {}
    _word = ""

    @_(r'\\n')
    def STR_CONST(self, t):
        t.value = self._word
        self.begin(L.CoolLexer)
        self._word = ""
        return t

    @_(r'.')
    def CONTENT(self, t):
        self._word += t.value

    def error(self, t):
        self.index += 1 # Avanza al siguiente caracter


'''
String lexer analyzer
'''
class Stringg(Lexer):
    tokens = {}
    _word = '"'

    """
    Caracteres que no se escapan
        \b backspace 
        \t tab
        \n newline 
        \f formfeed
    """
    @_(r'\\b')
    def BACKSPACE(self, t):
        self._word += r"\b"

    @_(r'\\t')
    def TAB(self, t):
        self._word += r"\t" # r"\\"+t.value

    @_(r'\\\n') # \.
    def OSC(self, t):
        print(self._word)
        print(t.value)
        self._word += r"\n"#t.value

    @_(r'\\n')
    def NEWLINE(self, t):
        self._word += r"\n"

    @_(r'\\f')
    def FORMFEED(self, t):
        self._word += r"\f"

    @_(r'"')
    def STR_CONST(self, t):
        self._word += '"'
        t.value = self._word
        self.begin(L.CoolLexer) # FIN
        self._word = '"'
        return t

    """"""

    @_(r'\\[A-Za-z0-9]') # Se elimina la \ de los caracteres o numeros
    def ONESLASH(self, t):
        print(t.value)
        self._word += t.value[-1]

    @_(r'\\\[A-Za-z0-9]') # \\.
    def TWOSLASH(self, t):
        print(t.value)
        self._word += t.value#[1:2]

    @_(r'\\.') # \.
    def ONESLASHCHARACT(self, t):
        self._word += t.value

    @_(r'.')
    def CHARACT(self, t):
        self._word += t.value

    """
    "A string may not contain EOF. 
        A string may not contain the null (character \0). 
        Any other character may be included in a string. 
        Strings cannot cross file boundaries."

    Caracteres no permitidos
        null (character \0)
        EOF
    """
    # TODO 

    def error(self, t):
        self.index += 1 # Avanza al siguiente caracter