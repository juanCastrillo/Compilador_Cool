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
    # TODO - Al reves
    # Si no se define una prioridad entonces se avanza siempre (seguir añadiendo a la pila)
    precedence = ( # Menos a mas importancia (prioridad)
        
        
        
        # ('right', 'UMINUS'), # UMINUS: - (cuando esta delante de una expresion, negativa)
        ('right', 'ASSIGN'),
        ('left', 'NOT'),
        ('left', 'LE', '<', '='),
        ('left', '+', '-'), 
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
    def clas(self, p): # TODO Comprobar que padre sea correcto
        return Clase(nombre=p[1], padre="Object", caracteristicas=p.feature_list, nombre_fichero=self.nombre_fichero)

    @_('CLASS TYPEID "{" "}"')
    def clas(self, p): # TODO Comprobar que padre sea correcto
        return Clase(nombre=p[1], padre="Object", caracteristicas=[], nombre_fichero=self.nombre_fichero)


    @_('CLASS TYPEID INHERITS TYPEID "{" feature_list "}"')
    def clas(self, p):
        return Clase(nombre=p[1], padre=p[3], caracteristicas=p.feature_list, nombre_fichero=self.nombre_fichero)

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
        return Metodo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr)

    @_('OBJECTID "(" formal_list ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr, formales=p.formal_list)

    @_('formal')
    def formal_list(self, p):
        return [p.formal]

    @_('formal_list "," formal')
    def formal_list(self, p):
        return p.formal_list + [p.formal]

    # ID:TYPE [ <- expr ]
    @_('OBJECTID ":" TYPEID ASSIGN expr')
    def feature(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr)

    @_('OBJECTID ":" TYPEID')
    def feature(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr())


    """
    FORMAL
    """
    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(nombre_variable=p.OBJECTID, tipo=p.TYPEID)


    """
    EXPR
    """
    @_('OBJECTID ASSIGN expr')
    def expr(self, p):
        return Asignacion(nombre=p[0], cuerpo=p[2])

    # expr[@TYPE].ID( [ expr [, expr]* ] )
    @_('OBJECTID "(" ")"') 
    def expr(self, p):
        return LlamadaMetodo(cuerpo=Objeto(nombre="self"), nombre_metodo=p.OBJECTID)
    
    @_('expr "." OBJECTID "(" ")"') 
    def expr(self, p):
        return LlamadaMetodo(cuerpo=p.expr, nombre_metodo=p.OBJECTID)

    @_('expr "@" TYPEID "." OBJECTID "(" ")"') 
    def expr(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expr, clase=p.TYPEID, nombre_metodo=p.OBJECTID)

    @_('expr "." OBJECTID "(" arg_list ")"') 
    def expr(self, p):
        return LlamadaMetodo(cuerpo=p.expr, nombre_metodo=p.OBJECTID, argumentos=p.arg_list)

    @_('expr "@" TYPEID "." OBJECTID "(" arg_list ")"')
    def expr(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expr, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=p.arg_list)

    @_('expr') # TODO - Quiza haya que incluir los parentesis aqui y no en el metodo de arriba
    def arg_list(self, p):
        return [p.expr]

    @_('arg_list "," expr') 
    def arg_list(self, p):
        return p[0] + [p.expr]
    ##

    #  ID( [ expr [, expr]* ] )
    @_(' OBJECTID "(" arg_list ")"') # TODO - cuerpo no existe
    def expr(self, p):
        return LlamadaMetodo(cuerpo=Objeto(nombre="self"), nombre_metodo=p.OBJECTID, argumentos=p.arg_list)

    # @_(' OBJECTID "(" ")"') 
    # def expr(self, p):
    #     return LlamadaMetodo(nombre_metodo=p.OBJECTID) 
    ##

    @_('IF expr THEN expr ELSE expr FI')
    def expr(self, p):
        return Condicional(condicion=p[1], verdadero=p[3], falso=p[5])

    @_('WHILE expr LOOP expr POOL')
    def expr(self, p):
        return Bucle(condicion=p[1], cuerpo=p[3])

    # { [expr; ]+ } Una o mas expresión entre llaves separadas por ;
    @_('"{" expresion_list "}"')
    def expr(self, p):
        return Bloque(expresiones=p.expresion_list)

    @_('expr ";"')
    def expresion_list(self, p):
        return [p.expr]

    @_('expresion_list expr ";"')
    def expresion_list(self, p):
        return p[0] + [p[1]]
    #    

    # TODO - Añadir valores a los opcionales (NoExpr())
    
    # let ID:TYPE [ <- expr ] [,ID:TYPE [ <- expr ]]* in expr
    @_('LET assign_list IN expr') #OBJECTID:TYPEID ,"OBJECTID":"TYPEID "[" ASSIGN expr "]""]""*" IN expr')
    def expr(self, p):
        x = p.expr
        for assignT in reversed(p.assign_list):
            x = Let(nombre=assignT[0], 
                tipo=assignT[1], inicializacion=assignT[2], cuerpo=x)
        return x

    # ID:TYPE [ <- expr ] [,ID:TYPE [ <- expr ]]*
    @_('OBJECTID ":" TYPEID ASSIGN expr')
    def assign_list(self, p):
        return [(p.OBJECTID, p.TYPEID, p.expr)]

    @_('OBJECTID ":" TYPEID')
    def assign_list(self, p):
        return [(p.OBJECTID, p.TYPEID, NoExpr())]

    @_('assign_list "," OBJECTID ":" TYPEID')
    def assign_list(self, p):
        return p.assign_list + [(p.OBJECTID, p.TYPEID, NoExpr())]

    @_('assign_list "," OBJECTID ":" TYPEID ASSIGN expr')
    def assign_list(self, p):
        return p.assign_list + [(p.OBJECTID, p.TYPEID, p.expr)]
    #

    # case expr of [ID : TYPE => expr; ]+ esac
    @_('CASE expr OF case_list ESAC')
    def expr(self, p):
        return Swicht(expr=p.expr, casos=p.case_list)

    @_('OBJECTID ":" TYPEID DARROW expr ";"')
    def case_list(self, p):
        return [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr)]

    @_('case_list OBJECTID ":" TYPEID DARROW expr ";"')
    def case_list(self, p):
        return p.case_list + [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr)]
    #

    @_("NEW TYPEID")
    def expr(self, p):
        return Nueva(tipo=p.TYPEID)

    @_("ISVOID expr")
    def expr(self, p):
        return EsNulo(expr=p.expr)

    @_('expr "+" expr')
    def expr(self, p):
        return Suma(izquierda=p[0], derecha=p[2])

    @_('expr "-" expr')
    def expr(self, p):
        return Resta(izquierda=p[0], derecha=p[2])

    @_('expr "*" expr')
    def expr(self, p):
        return Multiplicacion(izquierda=p[0], derecha=p[2])

    @_('expr "/" expr')
    def expr(self, p):
        return Division(izquierda=p[0], derecha=p[2])

    @_('"~" expr')
    def expr(self, p):
        return Neg(expr=p.expr)

    @_('expr "<" expr')
    def expr(self, p):
        return Menor(izquierda=p[0], derecha=p[2])

    @_('expr LE expr')
    def expr(self, p):
        return LeIgual(izquierda=p[0], derecha=p[2])

    @_('expr "=" expr')
    def expr(self, p):
        return Igual(izquierda=p[0], derecha=p[2])

    @_('NOT expr')
    def expr(self, p):
        return Not(expr=p.expr)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('OBJECTID')
    def expr(self, p):
        return Objeto(nombre=p.OBJECTID)

    @_('INT_CONST')
    def expr(self, p):
        return Entero(valor=p.INT_CONST)

    @_('STR_CONST')
    def expr(self, p):
        return String(valor=p.STR_CONST) 

    @_('BOOL_CONST')
    def expr(self, p):
        return Booleano(valor=p.BOOL_CONST)


    '''
    ERRORS
    # hay que añadir el keyword error en la string del método
    '''
    # @_('expr error') # TODO - Not working # badfeatures.test
    # def expresion_list(self, p):
    #     return [p.expr]

    # @_('expresion_list expr error') # TODO - Not working # badfeatures.test
    # def expresion_list(self, p):
    #     return p[0] + [p[1]]

    @_('error ";"')
    def expresion_list(self, p):
        return [] 

    # No puede hacer un bloque vacio {}
    @_('"{" error "}"')#@_('OBJECTID "(" ")" ":" TYPEID "{" error "}"')
    def feature(self, p):
        return Metodo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr())

    @_('formal_list error formal')
    def formal_list(self, p):
        return p.formal_list + [p.formal]

    # bar(x:Int;y:Int):Int {if true then 4 fi};
    @_('IF expr THEN expr ELSE expr error')
    def expr(self, p):
        return Condicional(condicion=p[1], verdadero=p[3], falso=p[5])

    @_('IF expr THEN expr error FI')
    def expr(self, p):
        return Condicional(condicion=p[1], verdadero=p[3], falso=p[5])

    # casenoexpr.test
    @_('CASE error OF case_list ESAC')
    def expr(self, p):
        return Swicht(expr=NoExpr(), casos=p.case_list)

    # bar():Int{{let a:Int<-Bork, b:Int<-5, c:Int<-6 in a + B;}};
    @_('OBJECTID ":" TYPEID ASSIGN error')
    def assign_list(self, p):
        return [(p.OBJECTID, p.TYPEID, NoExpr())]

    @_('assign_list "," OBJECTID ":" TYPEID ASSIGN error')
    def assign_list(self, p):
        return p.assign_list + [(p.OBJECTID, p.TYPEID, NoExpr())]

    @_('OBJECTID ":" error')
    def feature(self, p):
        return Atributo(nombre=p.OBJECTID, tipo="Object")

    @_('error ";"')
    def feature_list(self, p):
        return []

    # @_('feature_list feature error')
    # def feature_list(self, p):
    #     return p[0] + [p[1]]

    @_('CLASS TYPEID "{" error "}"')
    def clas(self, p): # TODO Comprobar que padre sea correcto
        return Clase(nombre=p[1], padre="Object", caracteristicas=[], nombre_fichero=self.nombre_fichero)

    # ID( [ formal [, formal]* ] ) : TYPE { expr }
    @_('OBJECTID "(" ")" ":" TYPEID "{" error "}"')
    def feature(self, p):
        return Metodo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr())

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
            # TODO - A;adir mensaje de error vacio
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
            # TODO - En funcion de lo que sea hay que cambiar el mensaje de error
            # TODO - En funcion de p.type
            # print(CoolLexer.literals)
            if p.type == "TYPEID" or p.type == "OBJECTID" or p.type == "INT_CONST":
                # "badblock.test", line 4: syntax error at or near TYPEID = A
                self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.type} = {p.value}')
            elif p.type in CoolLexer.literals : #p.value == "fi" or p.value == "else" or :
                self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near \'{p.value}\'')
            else:
                self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.value.upper()}')