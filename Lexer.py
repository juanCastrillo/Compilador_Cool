# coding: utf-8

from sly import Lexer
from OtherLexers import Comment, Stringg, Comment_Ml
import os
import re
import sys

class CoolLexer(Lexer): 
    '''
    Empieza en Apartado 10 del manual de Cool
    '''
    tokens = {
        OBJECTID, 
        INT_CONST, 
        BOOL_CONST, 
        TYPEID,
        ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
        INHERITS, ISVOID, LET, LOOP, NEW, OF,
        POOL, THEN, WHILE, NUMBER, 
        STR_CONST, # Cerrado entre "", hay que sustituir todos los caracteres ej: \c por c
            # excepto \b, \t, \n, \f
        LE, # Menor que 
        DARROW, # => 
        ASSIGN # <-
    }
    ignore = '\t '
    literals = {',', ';', ':', '@'}
    # Ejemplo
    ELSE = r'\b[eE][lL][sS][eE]\b'

    CARACTERES_CONTROL = [bytes.fromhex(i+hex(j)[-1]).decode('ascii')
                          for i in ['0', '1']
                          for j in range(16)] + [bytes.fromhex(hex(127)[-2:]).decode("ascii")]

    '''
    El analizador léxico otorga prioridad según su orden en el código 
    Se define un regex entre las comillas para indicar cuando llamar el método
    @_(r'')
    def TOKEN(self, t)
        ...
    '''
    @_(r'\n')
    def LINE(self, t):
        self.lineno += 1

    @_(r'[0-9]+')
    def INT_CONST(self, t): return t

    @_(r't[rR][uU][eE]|f[aA][lL][sS][eE]')
    def BOOL_CONST(self, t):
        return t

    """
    Palabras reservadas
    class, else, false, fi, if, in, 
    inherits, isvoid, let, loop, pool, then, while, case, esac, new, of, not, true

    ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
        INHERITS, ISVOID, LET, LOOP, NEW, OF,
        POOL, THEN, WHILE, NUMBER
    
    """
    @_(r'\b[eE][lL][sS][eE]\b')
    def ELSE(self, t): return t

    @_(r'\b[iI][fF]\b')
    def IF(self, t): return t

    @_(r'\b[fF][iI]\b')
    def FI(self, t): return t

    @_(r'\b[tT][hH][eE][nN]\b')
    def THEN(self, t): return t

    @_(r'\b[nN][oO][tT]\b')
    def NOT(self, t): return t

    @_(r'\b[iI][nN]\b')
    def IN(self, t): return t

    @_(r'\b[cC][aA][sS][eE]\b')
    def CASE(self, t): return t

    @_(r'\b[eE][sS][aA][cC]\b')
    def ESAC(self, t): return t

    @_(r'\b[cC][lL][aA][sS][sS]\b')
    def CLASS(self, t): return t

    @_(r'\b[iI][nN][hH][eE][rR][iI][tT][sS]\b')
    def INHERITS(self, t): return t

    @_(r'\b[iI][sS][vV][oO][iI][dD]\b')
    def ISVOID(self, t): return t

    @_(r'\b[lL][eE][tT]\b')
    def LET(self, t): return t

    @_(r'\b[lL][oO][oO][pP]\b')
    def LOOP(self, t): return t

    @_(r'\b[nN][eE][wW]\b')
    def NEW(self, t): return t

    @_(r'\b[oO][fF]\b')
    def OF(self, t): return t

    @_(r'\b[pP][oO][oO][lL]\b')
    def POOL(self, t): return t

    @_(r'\b[tT][hH][eE][nN]\b')
    def THEN(self, t): return t

    @_(r'\b[wW][hH][iI][lL][eE]\b')
    def WHILE(self, t): return t

    @_(r'\b[nN][uU][mM][bB][eE][rR]\b')
    def NUMBER(self, t): return t

    """"""

    """
    Simbolos
    LE, # Menor que 
        DARROW, # => 
        ASSIGN # <-
    """
    @_(r'<')
    def LE(self, t): return t

    @_(r'=>')
    def DARROW(self, t): return t
    
    @_(r'<-')
    def ASSIGN(self, t): return t

    """
    EXTRA
    """
    @_(r'[A-Z][A-Za-z0-9_]*')
    def TYPEID(self, t): return t

    @_(r'[a-z][A-Za-z0-9_]*')
    def OBJECTID(self, t): return t

    def error(self, t):
        # t.value = # Modificar el valor del ID a devolver
        self.index += 1 # Avanza al siguiente caracter
        #return t

    """
    Cambiar entre analizadores léxicos
    self.begin(NombreClaseAnalizador)
    """
    @_(r'"') # String
    def STR_CONST(self, t):
        self.begin(Stringg)

    @_(r'\(\*') # Comentario multilinea
    def COMMENT_ML(self, t):
        self.begin(Comment_Ml)

    @_(r'--') # Comentario una linea
    def COMMENT(self, t):
        self.begin(Comment)

    """
    Toma una cadena de texto
        texto: cadena de texto a analizar

    {returns: Lexification of the given text}
    """
    def salida(self, texto):
        list_strings = []
        lexer = self
        for token in lexer.tokenize(texto):
            result = f'#{token.lineno} {token.type} '
            if token.type == 'OBJECTID':
                result += f"{token.value}"
            elif token.type == 'BOOL_CONST':
                result += "true" if token.value else "false"
            elif token.type == 'TYPEID':
                result += f"{str(token.value)}"
            elif token.type in self.literals:
                result = f'#{token.lineno} \'{token.type}\' '
            elif token.type == 'STR_CONST':
                result += token.value
            elif token.type == 'INT_CONST':
                result += str(token.value)
            elif token.type == 'ERROR':
                result = f'#{token.lineno} {token.type} {token.value}'
            else:
                result = f'#{token.lineno} {token.type}'
            list_strings.append(result)
        return list_strings