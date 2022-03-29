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
    # Si no se define una prioridad entonces se avanza siempre (seguir añadiendo a la pila)
    precedence = ( # Menos a mas importancia (prioridad)
        ('left', '.'),
        ('left', '@'),
        ('left', '~'),
        ('left', 'ISVOID'),
        ('left', '*', '/'), # Los simbolos al mismo nivel tienen igual prioridad
        ('left', '+', '-'), 
        ('left', 'LE', '<', '=')
        # ('right', 'UMINUS'), # UMINUS: - (cuando esta delante de una expresion, negativa)
        ('left', 'NOT'),
        ('right', 'ASSIGN')
    )
    
    """
    program ::= [class; ]+

    class   ::= class TYPE [inherits TYPE] { [feature; ]* } 

    feature ::= ID( [ formal [, formal]* ] ) : TYPE { expr }
                ID:TYPE [ <- expr ] ::= ID : TYPE

    formal  ::= ID : TYPE

    expr    ::= ID <- expr
                expr[@TYPE].ID( [ expr [, expr]* ] ) ID( [ expr [, expr]* ] )
                if expr then expr else expr fi
                while expr loop expr pool
                { [expr; ]+ }
                let ID:TYPE [ <- expr ] [,ID:TYPE [ <- expr ]]* in expr case expr of [ID : TYPE => expr; ]+esac
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
    
    @_('class_list class ";"')
    def class_list(self, p):
        return p[0]+[p[1]]
    
    @_('clas ";"')
    def class_list(self, p):
        return [p[0]]

    """
    CLASS
    """
    @_('clas TYPEID "{" feature_list "}"')
    def clas(self, p): # TODO Comprobar que padre sea correcto
        return Clase(nombre=p[1], padre=Objeto(), caracteristicas=p.feature_list)

    @_('clas TYPEID INHERITS TYPEID "{" feature_list "}"')
    def clas(self, p):
        return Clase(nombre=p[1], padre=p[3], caracteristicas=p.feature_list)

    @_('feature ";"')
    def feature_list(self, p):
        return [p.feature]

    @_('feature_list feature ";"')
    def feature_list(self, p):
        return p[0] + [p[1]]


    """
    FEATURE
    """
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

    @_('expr"[""@"TYPEID]"."OBJECTID"(" "[" expr "[""," expr"]""*" "]" ")" OBJECTID"(" "[" expr "[""," expr"]""*" "]" ")"')
    def expr(self, p):

    @_('IF expr THEN expr ELSE expr FI')
    def expr(self, p):
        

    @_('WHILE expr LOOP expr POOL')
    def expr(self, p):

    @_('"{" "["expr";" "]""+" "}"')
    def expr(self, p):

    @_('LET OBJECTID:TYPEID "[" ASSIGN expr "]" "["","OBJECTID":"TYPEID "[" ASSIGN expr "]""]""*" IN expr CASE expr OF "["OBJECTID ":" TYPEID DARROW expr";" "]""+"ESAC')
    def expr(self, p):

    @_("NEW TYPEID")
    def expr(self, p):
        return Nueva(tipo=p.TYPEID)

    @_("ISVOID expr")
    def expr(self, p):

    @_('expr "+" expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr "-" expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr "*" expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr "/" expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('"~"expr')
    def expr(self, p):

    @_('expr "<" expr')
    def expr(self, p):
        return p.expr0 < p.expr1

    @_('expr DARROW expr')
    def expr(self, p):
        # return p.expr0 <= p.expr1

    @_('expr "=" expr')
    def expr(self, p):
        return p.expr0 == p.expr1

    @_('NOT expr')
    def expr(self, p):

    @_('"(" expr ")"')
    def expr(self, p):

    @_('OBJECTID')
    def expr(self, p):
        return p.expr

    @_('INT_CONST')
    def expr(self, p):
        return p.INT_CONST

    @_('SRT_CONST')
    def expr(self, p):

    @_('BOOL_CONST'):
    def expr(self, p):