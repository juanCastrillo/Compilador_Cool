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

    '''
    When EOF is reached inside the comment
    '''
    @_(r'[^*)]$') # EOF
    def BADEND(self, t):
        t.type = "ERROR"
        t.value = '"EOF in comment"'
        self._word = '"'
        self.begin(L.CoolLexer)
        return t
        
    '''
    If a comment is closed and EOF is reached 
    but theres still comment nesting to close.
    '''
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

    '''
    Starts a new comment, nesting it
    '''
    @_(r'\(\*')
    def ANOTHERONE(self, t):
        self.commentCount += 1

    '''
    Closes the current comment
    '''
    @_(r'\*\)')
    def STR_CONST(self, t):
        self.commentCount -= 1
        if self.commentCount < 1:
            self.commentCount = 1
            self.begin(L.CoolLexer)

    '''
    Increases the line count
    '''
    @_(r'\n')
    def NEXTLINE(self, t):
        self.lineno += 1

    '''
    Ignore everything not closing the comment
    '''
    @_(r'.')
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

    '''
    End of the single line comment
    '''
    @_(r'\n')
    def STR_CONST(self, t):
        t.value = self._word
        self._word = ""
        self.begin(L.CoolLexer)
        self.lineno += 1
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

    # SALIDA
    @_(r'"')
    def STR_CONST(self, t):
        self._word += '"'
        
        if self._nChars > 1024: 
            # print(len(self._word))
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


    """
    Caracteres que no se escapan
        \b backspace 
        \t tab
        \n newline 
        \f formfeed
    """
    @_(r'\\x08|\\\x08|\\b')
    def BACKSPACE(self, t):
        self._nChars += 1
        self._word += r"\b"

    @_(r'\\t|\t', r'\\\t') # \\\t quiza haya que hacer solo la \ y hacer match de \\t?
    def TAB(self, t):
        self._nChars += 1
        self._word += r"\t" # r"\\"+t.value

    @_(r'\\\n|\\n') # Escapar un \n es añadir un literal \n
    def NEWLINE1(self, t):
        self._nChars += 1
        self.lineno += 1 # TODO - Revisar que el salto de linea correcto es este y no uno escapado
        self._word += r"\n"
        # self.error(t)

    @_(r'\f|\\f', r'\\\f')
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

    @_(r'\015|\\015')
    def CRETURN(self, t):
        self._nChars += 1
        self._word += r"\015"

    @_(r'\033|\\033')
    def ESCAPE1(self, t):
        self._nChars += 1
        self._word += r"\033"

    # @_(r"\\[^\\]")
    # def SLASHBAD(self, t):
    #     t.type = "ERROR"
    #     t.value = r'"\\"'
    #     self._word = '"'
    #     _nChars = 0
    #     self.begin(L.CoolLexer)
    #     return t

    """
    ERRORS
    "A string may not contain EOF. 
        A string may not contain the null (character \0). 
        Any other character may be included in a string. 
        Strings cannot cross file boundaries."

    Caracteres no permitidos
        null (character \0)
        EOF
    """
    @_('\n') # error
    def NEWLINE2(self, t):
        t.type = "ERROR"
        t.value = '"Unterminated string constant"'
        self._word = '"'
        self.begin(L.CoolLexer)
        return t

    @_(r'\0[^"\n]*"?') # error
    def NULLCHAR1(self, t):
        t.type = "ERROR" 
        t.value = '"String contains null character."'
        self._word = '"'
        _nChars = 0
        self.begin(L.CoolLexer)
        return t

    
    @_(r'\\\0[^"]*"?') # error
    def NULLCHAR2(self, t):
        t.type = "ERROR" 
        t.value = '"String contains escaped null character."'
        self._word = '"'
        _nChars = 0
        self.begin(L.CoolLexer)
        return t


    @_(r'[^"]\Z', r'[^"]\\Z', r'[^"]\\\Z', r'[^"]\\\\Z')
    def EOFERROR1(self, t):
        # print("ola1")
        t.type = "ERROR"
        t.value = '"EOF in string constant"'
        self._word = '"'
        _nChars = 0
        self.begin(L.CoolLexer)
        return t

    @_(r'[^"]\\$',r'[^"]\\\$', r'\\"$',) # EOF error
    def EOFERROR2(self, t):
        t.type = "ERROR"
        t.value = '"EOF in string constant"'
        self._word = '"'
        _nChars = 0
        self.begin(L.CoolLexer)
        return t

    


    '''
    Caracteres regulares
    '''
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

    @_(r'\\-')
    def ONESSLASHCHARACT2(self, t):
        self._nChars += 1
        self._word += "-"

    @_(r'\\.') # \.
    def ONESLASHCHARACT(self, t):
        self._nChars += 1
        self._word += t.value

    @_(r'.')
    def CHARACT(self, t):
        self._nChars += 1
        self._word += t.value



    
    def error(self, t):
        self.index += 1 # Avanza al siguiente caracter
        print("error")
        t.type = "ERROR"
        # t.value = '"Unterminated string constant"'
        self._word = '"'
        _nChars = 0
        self.begin(L.CoolLexer)
        return t