# coding: utf-8

from Lexer import CoolLexer
from sly import Parser
import sys
import os
from Clases import *

"""
Parser de Cool
"""
class CoolParser(Parser):
    nombre_fichero = ''
    tokens = CoolLexer.tokens
    debugfile = "salida.out"
    errores = []

    """
    .
    @
    ~ 
    isvoid 
    * / 
    + -
    <= < = 
    not
    <-
    """
    # from highest to lowest 
    # Si no se define una prioridad entonces se avanza siempre (seguir añadiendo a la pila)
    precedence = ( # Menos a mas importancia (prioridad)
        
        
        
        # ('right', 'UMINUS'), # UMINUS: - (cuando esta delante de una expresion, negativa)
        ('right', 'ASSIGN'),
        ('left', 'NOT'),
        ('right', 'LE', '<', '='),
        ('left', '+', '-'), # Left
        ('left', '*', '/'), # Los simbolos al mismo nivel tienen igual prioridad
        ('left', 'ISVOID'),
        ('left', '~'),
        ('left', '@'),
        ('left', '.'),
    )
    
    """
    program ::= [class; ]+

    class   ::= class TYPE [inherits TYPE] { [feature; ]* } 

    feature ::= ID( [ formal [, formal]* ] ) : TYPE { expr }
                ID:TYPE [ <- expr ]

    formal  ::= ID : TYPE

    expr    ::= ID <- expr
                expr[@TYPE].ID( [ expr [, expr]* ] ) 
                ID( [ expr [, expr]* ] )
                if expr then expr else expr fi
                while expr loop expr pool
                { [expr; ]+ }
                let ID:TYPE [ <- expr ] [,ID:TYPE [ <- expr ]]* in expr 
                case expr of [ID : TYPE => expr; ]+esac
                new TYPE
                isvoid expr
                expr + expr
                expr - expr
                expr * expr
                expr / expr
                ~expr
                expr < expr
                expr <= expr
                expr = expr
                not expr
                (expr)
                ID
                integer
                string
                true
                false
    """
    # Replaced
    # return ([A-Z][a-z]*.+)\)
    # return $1, linea=p.lineno)
    """
    PROGRAM
    """
    @_('class_list')
    def program(self, p):        
        return Programa(secuencia=p.class_list)
    
    @_('class_list clas ";"')
    def class_list(self, p):
        return p[0]+[p[1]]
    
    @_('clas ";"')
    def class_list(self, p):
        return [p[0]]

    """
    CLASS
    """
    @_('CLASS TYPEID "{" feature_list "}"')
    def clas(self, p): 
        return Clase(nombre=p[1], padre="Object", caracteristicas=p.feature_list, nombre_fichero=self.nombre_fichero, linea=p.lineno)

    @_('CLASS TYPEID "{" "}"')
    def clas(self, p): 
        return Clase(nombre=p[1], padre="Object", caracteristicas=[], nombre_fichero=self.nombre_fichero, linea=p.lineno)


    @_('CLASS TYPEID INHERITS TYPEID "{" feature_list "}"')
    def clas(self, p):
        return Clase(nombre=p[1], padre=p[3], caracteristicas=p.feature_list, nombre_fichero=self.nombre_fichero, linea=p.lineno)

    @_('CLASS TYPEID INHERITS TYPEID "{" "}"')
    def clas(self, p): 
        return Clase(nombre=p[1], padre=p[3], caracteristicas=[], nombre_fichero=self.nombre_fichero, linea=p.lineno)


    @_('feature ";"')
    def feature_list(self, p):
        return [p.feature]

    @_('feature_list feature ";"')
    def feature_list(self, p):
        return p[0] + [p[1]]


    """
    FEATURE
    """
    # ID( [ formal [, formal]* ] ) : TYPE { expr }
    @_('OBJECTID "(" ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr, linea=p.lineno)

    @_('OBJECTID "(" formal_list ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr, formales=p.formal_list, linea=p.lineno)

    @_('formal')
    def formal_list(self, p):
        return [p.formal]

    @_('formal_list "," formal')
    def formal_list(self, p):
        return p.formal_list + [p.formal]

    # ID:TYPE [ <- expr ]
    @_('OBJECTID ":" TYPEID ASSIGN expr')
    def feature(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr, linea=p.lineno)

    @_('OBJECTID ":" TYPEID')
    def feature(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr(), linea=p.lineno)


    """
    FORMAL
    """
    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(nombre_variable=p.OBJECTID, tipo=p.TYPEID, linea=p.lineno)


    """
    EXPR
    """
    @_('OBJECTID ASSIGN expr')
    def expr(self, p):
        return Asignacion(nombre=p[0], cuerpo=p[2], linea=p.lineno)

    # expr[@TYPE].ID( [ expr [, expr]* ] )
    @_('OBJECTID "(" ")"') 
    def expr(self, p):
        return LlamadaMetodo(cuerpo=Objeto(nombre="self"), nombre_metodo=p.OBJECTID, linea=p.lineno)
    
    @_('expr "." OBJECTID "(" ")"') 
    def expr(self, p):
        return LlamadaMetodo(cuerpo=p.expr, nombre_metodo=p.OBJECTID, linea=p.lineno)

    @_('expr "@" TYPEID "." OBJECTID "(" ")"') 
    def expr(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expr, clase=p.TYPEID, nombre_metodo=p.OBJECTID, linea=p.lineno)

    @_('expr "." OBJECTID "(" arg_list ")"') 
    def expr(self, p):
        return LlamadaMetodo(cuerpo=p.expr, nombre_metodo=p.OBJECTID, argumentos=p.arg_list, linea=p.lineno)

    @_('expr "@" TYPEID "." OBJECTID "(" arg_list ")"')
    def expr(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expr, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=p.arg_list, linea=p.lineno)

    @_('expr')
    def arg_list(self, p):
        return [p.expr]

    @_('arg_list "," expr') 
    def arg_list(self, p):
        return p[0] + [p.expr]
    ##

    #  ID( [ expr [, expr]* ] )
    @_(' OBJECTID "(" arg_list ")"')
    def expr(self, p):
        return LlamadaMetodo(cuerpo=Objeto(nombre="self"), nombre_metodo=p.OBJECTID, argumentos=p.arg_list, linea=p.lineno)

    # @_(' OBJECTID "(" ")"') 
    # def expr(self, p):
    #     return LlamadaMetodo(nombre_metodo=p.OBJECTID, linea=p.lineno) 
    ##

    @_('IF expr THEN expr ELSE expr FI')
    def expr(self, p):
        return Condicional(condicion=p[1], verdadero=p[3], falso=p[5], linea=p.lineno)

    @_('WHILE expr LOOP expr POOL')
    def expr(self, p):
        return Bucle(condicion=p[1], cuerpo=p[3], linea=p.lineno)

    # { [expr; ]+ } Una o mas expresión entre llaves separadas por ;
    @_('"{" expresion_list "}"')
    def expr(self, p):
        return Bloque(expresiones=p.expresion_list, linea=p.lineno)

    @_('expr ";"')
    def expresion_list(self, p):
        return [p.expr]

    @_('expresion_list expr ";"')
    def expresion_list(self, p):
        return p[0] + [p[1]]
    
    # let ID:TYPE [ <- expr ] [,ID:TYPE [ <- expr ]]* in expr
    @_('LET assign_list IN expr') #OBJECTID:TYPEID ,"OBJECTID":"TYPEID "[" ASSIGN expr "]""]""*" IN expr')
    def expr(self, p):
        x = p.expr
        for assignT in reversed(p.assign_list):
            x = Let(nombre=assignT[0], 
                tipo=assignT[1], inicializacion=assignT[2], cuerpo=x, linea=p[3])
        return x

    # ID:TYPE [ <- expr ] [,ID:TYPE [ <- expr ]]*
    @_('OBJECTID ":" TYPEID ASSIGN expr')
    def assign_list(self, p):
        return [(p.OBJECTID, p.TYPEID, p.expr, p.lineno)]

    @_('OBJECTID ":" TYPEID')
    def assign_list(self, p):
        return [(p.OBJECTID, p.TYPEID, NoExpr(), p.lineno)]

    @_('assign_list "," OBJECTID ":" TYPEID')
    def assign_list(self, p):
        return p.assign_list + [(p.OBJECTID, p.TYPEID, NoExpr(), p.lineno)]

    @_('assign_list "," OBJECTID ":" TYPEID ASSIGN expr')
    def assign_list(self, p):
        return p.assign_list + [(p.OBJECTID, p.TYPEID, p.expr, p.lineno)]
    #

    # case expr of [ID : TYPE => expr; ]+ esac
    @_('CASE expr OF case_list ESAC')
    def expr(self, p):
        return Switch(expr=p.expr, casos=p.case_list, linea=p.lineno)

    @_('OBJECTID ":" TYPEID DARROW expr ";"')
    def case_list(self, p):
        return [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr)]

    @_('case_list OBJECTID ":" TYPEID DARROW expr ";"')
    def case_list(self, p):
        return p.case_list + [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr, linea=p.lineno)]
    #

    @_("NEW TYPEID")
    def expr(self, p):
        return Nueva(tipo=p.TYPEID, linea=p.lineno)

    @_("ISVOID expr")
    def expr(self, p):
        return EsNulo(expr=p.expr, linea=p.lineno)

    @_('expr "+" expr')
    def expr(self, p):
        return Suma(izquierda=p[0], derecha=p[2], linea=p.lineno)

    @_('expr "-" expr')
    def expr(self, p):
        return Resta(izquierda=p[0], derecha=p[2], linea=p.lineno)

    @_('expr "*" expr')
    def expr(self, p):
        return Multiplicacion(izquierda=p[0], derecha=p[2], linea=p.lineno)

    @_('expr "/" expr')
    def expr(self, p):
        return Division(izquierda=p[0], derecha=p[2], linea=p.lineno)

    @_('"~" expr')
    def expr(self, p):
        return Neg(expr=p.expr, linea=p.lineno)

    @_('expr "<" expr')
    def expr(self, p):
        return Menor(izquierda=p[0], derecha=p[2], linea=p.lineno)

    @_('expr LE expr LE expr')
    def expr(self, p):
        self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near LE')
        # self.error(p)

    @_('expr LE expr')
    def expr(self, p):
        return LeIgual(izquierda=p[0], derecha=p[2], linea=p.lineno)

    @_('expr "=" expr "=" expr')
    def expr(self, p):
        self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near \'=\'')
        # self.error(p)

    @_('expr "=" expr')
    def expr(self, p):
        return Igual(izquierda=p[0], derecha=p[2], linea=p.lineno)

    @_('NOT expr')
    def expr(self, p):
        return Not(expr=p.expr, linea=p.lineno)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('OBJECTID')
    def expr(self, p):
        return Objeto(nombre=p.OBJECTID, linea=p.lineno)

    @_('INT_CONST')
    def expr(self, p):
        return Entero(valor=p.INT_CONST, linea=p.lineno)

    @_('STR_CONST')
    def expr(self, p):
        return String(valor=p.STR_CONST, linea=p.lineno) 

    @_('BOOL_CONST')
    def expr(self, p):
        return Booleano(valor=p.BOOL_CONST, linea=p.lineno)


    '''
    ERRORS
    '''

   

    @_('error ";"')
    def expresion_list(self, p):
        return [] 

    # No puede hacer un bloque vacio {}
    @_('"{" error "}"')#@_('OBJECTID "(" ")" ":" TYPEID "{" error "}"')
    def feature(self, p):
        return Metodo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr(), linea=p.lineno)

    @_('formal_list error formal')
    def formal_list(self, p):
        return p.formal_list + [p.formal]

    # bar(x:Int;y:Int):Int {if true then 4 fi};
    @_('IF expr THEN expr ELSE expr error')
    def expr(self, p):
        return Condicional(condicion=p[1], verdadero=p[3], falso=p[5], linea=p.lineno)

    @_('IF expr THEN expr error FI')
    def expr(self, p):
        return Condicional(condicion=p[1], verdadero=p[3], falso=p[5], linea=p.lineno)

    # casenoexpr.test
    @_('CASE error OF case_list ESAC')
    def expr(self, p):
        return Switch(expr=NoExpr(), casos=p.case_list, linea=p.lineno)

    # bar():Int{{let a:Int<-Bork, b:Int<-5, c:Int<-6 in a + B;}};
    @_('OBJECTID ":" TYPEID ASSIGN error')
    def assign_list(self, p):
        return [(p.OBJECTID, p.TYPEID, NoExpr())]

    @_('assign_list "," OBJECTID ":" TYPEID ASSIGN error')
    def assign_list(self, p):
        return p.assign_list + [(p.OBJECTID, p.TYPEID, NoExpr(), p.lineno)]

    @_('OBJECTID ":" error')
    def feature(self, p):
        return Atributo(nombre=p.OBJECTID, tipo="Object", linea=p.lineno)

    @_('error ";"')
    def feature_list(self, p):
        return []

    # @_('feature_list feature error')
    # def feature_list(self, p):
    #     return p[0] + [p[1]]

    @_('CLASS TYPEID "{" error "}"')
    def clas(self, p): 
        return Clase(nombre=p[1], padre="Object", caracteristicas=[], nombre_fichero=self.nombre_fichero, linea=p.lineno)

    # ID( [ formal [, formal]* ] ) : TYPE { expr }
    @_('OBJECTID "(" ")" ":" TYPEID "{" error "}"')
    def feature(self, p):
        return Metodo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr(), linea=p.lineno)

    @_('feature error')
    def feature_list(self, p):
        return [p.feature]

    @_('feature_list feature error')
    def feature_list(self, p):
        return p[0] + [p[1]]

    def error(self, p):
        # line 3: syntax error at or near ':'
        # Token(type='TYPEID', value='A', lineno=4, index=40)
        if not p:
            # "emptyprogram.test", line 0: syntax error at or near EOF
            self.errores.append(f'"{self.nombre_fichero}", line 0: syntax error at or near EOF')
        else:
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
                LE, # <=
                DARROW, # => 
                ASSIGN # <-
            }
            '''
            # print(CoolLexer.literals)
            if p.type == "TYPEID" or p.type == "OBJECTID" or p.type == "INT_CONST":
                # "badblock.test", line 4: syntax error at or near TYPEID = A
                self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.type} = {p.value}')
            elif p.type in CoolLexer.literals : #p.value == "fi" or p.value == "else" or :
                self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near \'{p.value}\'')
            else:
                self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.value.upper()}')