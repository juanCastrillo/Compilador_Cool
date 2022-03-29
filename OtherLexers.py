from distutils.log import error
from sly import Lexer
import Lexer as L

'''
Multiline comment lexer analyzer
(* *)
'''
class Comment_Ml(Lexer):
    tokens = {}
    commentCount = 1

    @_(r'[^"]$', r'[^"]\$', r'[^"]\\$', r'[^"]\\\$') # EOF
    def EOFERROR4(self, t):
        print("ola4", t.value)
        t.type = "ERROR"
        t.value = '"EOF in comment"'
        self._word = '"'
        self.begin(L.CoolLexer)
        

    @_(r'\(\*')
    def ANOTHERONE(self, t):
        self.commentCount += 1

    @_(r'\\*\)')
    def ESCAPED(self, t):
        pass

    @_(r'^(\*\))\Z', r'^(\*\))\\Z', r'^(\*\))\\\Z', r'^(\*\))\\\\Z')
    def BADEND(self, t):
        t.type = "ERROR"
        t.value = '"EOF in comment"'
        # self.commentCount -= 1
        # if self.commentCount < 1:
        #     self.commentCount = 1
        self.begin(L.CoolLexer)
        return t

    @_(r'\*\)$')
    def BADEND2(self, t):
        self.commentCount -= 1
        if self.commentCount < 1:
           
            self.commentCount = 1
            self.begin(L.CoolLexer)
        else:
            t.type = "ERROR"
            t.value = '"EOF in comment"'
            return t

    @_(r'\*\)')
    def STR_CONST(self, t):
        self.commentCount -= 1
        if self.commentCount < 1:
            self.commentCount = 1
            self.begin(L.CoolLexer)

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

    # @_(r'\\n')
    # def STR_CONST(self, t):
    #     t.value = self._word
    #     self._word = ""
    #     self.begin(L.CoolLexer)

    @_(r'\n')
    def STR_CONST(self, t):
        t.value = self._word
        self._word = ""
        self.begin(L.CoolLexer)
        
        #return t

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
    errors = False
    _nChars = 0

    """
    Caracteres que no se escapan
        \b backspace 
        \t tab
        \n newline 
        \f formfeed
    """
    @_(r'\\b')
    def BACKSPACE(self, t):
        self._nChars += 1
        self._word += r"\b"

    @_(r'\\t|\t')
    def TAB(self, t):
        self._nChars += 1
        self._word += r"\t" # r"\\"+t.value

    @_(r'\\\n|\\n') # Escapar un \n es añadir un literal \n
    def NEWLINE1(self, t):
        self._nChars += 1
        self._word += r"\n"
        # self.error(t)

    @_('\n') # error
    def NEWLINE2(self, t):
        t.type = "ERROR"
        t.value = '"Unterminated string constant"'
        self._word = '"'
        self.begin(L.CoolLexer)
        return t

    @_(r'\0[^"]*"?') # error
    def NULLCHAR1(self, t):
        t.type = "ERROR" 
        t.value = '"String contains null character."'
        self._word = '"'
        _nChars = 0
        self.begin(L.CoolLexer)
        return t

    # @_(r'[^"]$') # EOF error
    @_(r'[^"]\Z', r'[^"]\\Z', r'[^"]\\\Z', r'[^"]\\\\Z')
    def EOFERROR1(self, t):
        print("ola1")
        t.type = "ERROR"
        t.value = '"EOF in string constant"'
        self._word = '"'
        _nChars = 0
        self.begin(L.CoolLexer)
        return t

    @_(r'\f|\\f')
    def FORMFEED(self, t):
        self._nChars += 1
        self._word += r"\f"

    # \f\022\013
    @_(r'\022|\\022')
    def BLANK1(self, t):
        self._nChars += 1
        self._word += r"\022"

    @_(r'\013|\\013')
    def BLANK2(self, t):
        self._nChars += 1
        self._word += r"\013"

    # SALIDA
    @_(r'"')
    def STR_CONST(self, t):
        self._word += '"'
        
        if self._nChars > 1024: 
            print(len(self._word))
            t.type = "ERROR"
            t.value = '"String constant too long"'
        else:
            t.value = self._word
            if self._word[0] != '"':
                t.value = '"'+t.value
            if len(self._word) == 1:
                t.value = '""'
            
        self._word = '"'
        self._nChars = 0

        self.begin(L.CoolLexer)
        return t
        
    """"""

    @_(r'\\[A-Za-z0-9]') # Se elimina la \ de los caracteres o numeros
    def ONESLASH(self, t):
        # print(t.value)
        self._nChars += 1
        self._word += t.value[-1]

    @_(r'\\\[A-Za-z0-9]') # \\.
    def TWOSLASH(self, t):
        # print(t.value)
        self._nChars += 1
        self._word += t.value#[1:2]

    @_(r'\\.') # \.
    def ONESLASHCHARACT(self, t):
        # print(t.value)
        self._nChars += 1
        self._word += t.value

    @_(r'.')
    def CHARACT(self, t):
        # print(t.value)
        self._nChars += 1
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
    def error(self, t):
        self.index += 1 # Avanza al siguiente caracter
        print("error")
        t.type = "ERROR"
        t.value = '"Unterminated string constant"'
        self._word = '"'
        _nChars = 0
        self.begin(L.CoolLexer)
        return t