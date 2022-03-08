from sly import Lexer
import Lexer as L

'''
Multiline comment lexer analyzer
(* *)
'''
class Comment_Ml(Lexer):
    tokens = {}
    commentCount = 1

    @_(r'\(\*')
    def ANOTHERONE(self, t):
        self.commentCount += 1

    @_(r'\\*\)')
    def ESCAPED(self, t):
        pass

    @_(r'\*\)')
    def STR_CONST(self, t):
        self.commentCount -= 1
        if self.commentCount < 1:
            self.commentCount = 1
            self.begin(L.CoolLexer)
        
        #return t

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

    @_(r'\\t|\t')
    def TAB(self, t):
        self._word += r"\t" # r"\\"+t.value



    # @_(r'\\\n') # \.
    # def OSC(self, t):
    #     # # print(self._word)
    #     # # print(t.value)
    #     self._word += r"\n"#t.value

    @_(r'\\\n|\\n') # Escapar un \n es añadir un literal \n
    def NEWLINE1(self, t):
        self._word += r"\n"
        # self.error(t)

    @_('\n') # error
    def NEWLINE2(self, t):
        # self._word += r"\n"
        
        # self.errors = True
        t.type = "ERROR"
        t.value = '"Unterminated string constant"'
        self._word = '"'
        self.begin(L.CoolLexer)
        return t

    @_(r'\\\0') # error
    def NULLCHAR(self, t):
        # self._word += r"\n"
        # self.error(t)
        # self.errors = True
        t.type = "ERROR"  
        t.value = '"String contains escaped null character."'
        self._word = '"'
        self.begin(L.CoolLexer)
        return t

    @_(r'\\0') # error
    def NULLCHAR(self, t):
        # self._word += r"\n"
        # self.error(t)
        # self.errors = True
        t.type = "ERROR"  
        t.value = '"String contains escaped null character."'
        self._word = '"'
        self.begin(L.CoolLexer)
        return t

    @_(r'\0') # error
    def NULLCHAR(self, t):
        # self._word += r"\n"
        # self.error(t)
        # self.errors = True
        t.type = "ERROR" 
        t.value = '"String contains escaped null character."'
        self._word = '"'
        self.begin(L.CoolLexer)
        return t
    
    @_(r'[^"]$') # EOF error
    def EOFERROR(self, t):
        t.type = "ERROR"
        t.value = '"EOF in string constant"'
        self._word = '"'
        self.begin(L.CoolLexer)
        return t


    @_(r'\\f')
    def FORMFEED(self, t):
        self._word += r"\f"

    @_(r'"')
    def STR_CONST(self, t):
        self._word += '"'
        
        if len(self._word) > 2050: 
            print(len(self._word))
            t.type = "ERROR"
            t.value = '"String constant too long"'
            self._word = '"'
        else:
            t.value = self._word
            if self._word[0] != '"':
                t.value = '"'+t.value
            if len(self._word) == 1:
                t.value = '""'
            self._word = '"'
            self.errors = False

        self.begin(L.CoolLexer) # FIN
            
        return t
        
    """"""

    @_(r'\\[A-Za-z0-9]') # Se elimina la \ de los caracteres o numeros
    def ONESLASH(self, t):
        # print(t.value)
        self._word += t.value[-1]

    @_(r'\\\[A-Za-z0-9]') # \\.
    def TWOSLASH(self, t):
        # print(t.value)
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
        print("error")
        t.type = "ERROR"
        t.value = '"Unterminated string constant"'
        self._word = '"'
        self.begin(L.CoolLexer)
        return t