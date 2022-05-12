# coding: utf-8
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List

errores_tipo = []

class CodeError(Exception):
    pass

@dataclass
class Nodo:
    linea: int = 0

    def str(self, n):
        return f'{n*" "}#{self.linea}\n'


@dataclass
class Formal(Nodo):
    nombre_variable: str = '_no_set'
    tipo: str = '_no_type'

    def TIPO(self, ambito):
        self.cast = self.tipo

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_formal\n'
        resultado += f'{(n+2)*" "}{self.nombre_variable}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        return resultado


class Expresion(Nodo):
    cast: str = '_no_type'

    def TIPO(self, ambito):
        pass


@dataclass
class Asignacion(Expresion):
    nombre: str = '_no_set'
    cuerpo: Expresion = None

    def TIPO(self, ambito):
        self.cuerpo.TIPO(ambito)
        sc = self.cuerpo.cast
        t = ambito.tipoVar(self.nombre) 
        if t != sc:
            raise CodeError(f"Tipo de asignación no coincide con el designado para la variable: {t} != {sc}")
            # cells <- (new CellularAutomaton).init("         X         ");

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_assign\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class LlamadaMetodoEstatico(Expresion):
    cuerpo: Expresion = None
    clase: str = '_no_type'
    nombre_metodo: str = '_no_set'
    argumentos: List[Expresion] = field(default_factory=list)

    def TIPO(self, ambito):
        # TODO - No entiendo la sintaxis del metodo estatico.
        
        # Copiado de LlamadaMetodo
        self.cuerpo.TIPO(ambito)
        argsFirma = ambito.argumentos(self.clase, self.nombre_metodo)
    
        tipo = argsFirma[-1]
        args = argsFirma[:-1]
 
        for arg, argF in zip(self.argumentos, args): # Compruebo que el tipo de los argumentos pasados sea el correcto
            arg.TIPO(ambito)
            if arg.cast != argF:
                raise CodeError(f"El tipo del argumento no coincide con el esperado: {arg.cast} != {argF}")
        self.cast = tipo

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_static_dispatch\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n+2)*" "}{self.clase}\n'
        resultado += f'{(n+2)*" "}{self.nombre_metodo}\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.argumentos])
        resultado += f'{(n+2)*" "})\n'
        resultado += f'{(n)*" "}: _no_type\n'
        return resultado


@dataclass
class LlamadaMetodo(Expresion):
    cuerpo: Expresion = None
    nombre_metodo: str = '_no_set'
    argumentos: List[Expresion] = field(default_factory=list)

    def TIPO(self, ambito):
        self.cuerpo.TIPO(ambito)
        argsFirma = ambito.argumentos(self.cuerpo.cast, self.nombre_metodo)
        # TODO - Ver si el metodo existe antes de llamarlo
    
        tipo = argsFirma[-1]
        args = argsFirma[:-1]
        # if tipo == ('map', 'String'):
        #     print(1)
        for arg, argF in zip(self.argumentos, args): # Compruebo que el tipo de los argumentos pasados sea el correcto
            arg.TIPO(ambito)
            if arg.cast != argF:
                raise CodeError(f"El tipo del argumento no coincide con el esperado: {arg.cast} != {argF}")
        self.cast = tipo
        '''
        def argumentos(self, clase, metodo):
            claseOriginal = clase
            while (clase, metodo) not in self.metodos: #
                clase = self.padre(clase)
            tipo = self.metodos[clase, metodo][-1]
            if tipo == "SELF_TYPE":
                tipo = claseOriginal
            return self.metodos[clase, metodo][:-1]+[tipo]
        '''

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_dispatch\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n+2)*" "}{self.nombre_metodo}\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.argumentos])
        resultado += f'{(n+2)*" "})\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Condicional(Expresion):
    condicion: Expresion = None
    verdadero: Expresion = None
    falso: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_cond\n'
        resultado += self.condicion.str(n+2)
        resultado += self.verdadero.str(n+2)
        resultado += self.falso.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Bucle(Expresion):
    condicion: Expresion = None
    cuerpo: Expresion = None

    def TIPO(self, ambito):
        self.condicion.TIPO(ambito)
        if self.condicion.cast != "Bool":
            raise CodeError("Condición del bucle while no es un Bool.")
        self.cuerpo.TIPO(ambito)
        self.cast = self.cuerpo.cast

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_loop\n'
        resultado += self.condicion.str(n+2)
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Let(Expresion):
    nombre: str = '_no_set'
    tipo: str = '_no_set'
    inicializacion: Expresion = None
    cuerpo: Expresion = None

    def TIPO(self, ambito):
        # TODO - todos los cuerpos del let comparten ambito o va para arriba o va para abajo
        # TODO - Las variables del let se comparten con el exterior?
        # El cuerpo tiene el nuevo ambito para evaluar el nombre tipo e inicializacion\
        # let nombre:tipo in 
        #   let nombre2:tipo2 in
        #       let ...
        nuevoAmbito = deepcopy(ambito)
        cuerpo = self.cuerpo
        nuevoAmbito.addVar(self.nombre,self.tipo)
        if isinstance(cuerpo, Let):
            nuevoAmbito.addVar(cuerpo.nombre, cuerpo.tipo)
            cuerpo = cuerpo.cuerpo
            
        cuerpo.TIPO(nuevoAmbito)
        self.cast = cuerpo.cast

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_let\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.inicializacion.str(n+2)
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Bloque(Expresion):
    expresiones: List[Expresion] = field(default_factory=list)

    def TIPO(self, ambito):
        nuevoAmbito = deepcopy(ambito)
        for expresion in self.expresiones:
            expresion.TIPO(nuevoAmbito)
        self.cast = self.expresiones[-1].cast 

    def str(self, n):
        resultado = super().str(n)
        resultado = f'{n*" "}_block\n'
        resultado += ''.join([e.str(n+2) for e in self.expresiones])
        resultado += f'{(n)*" "}: {self.cast}\n'
        resultado += '\n'
        return resultado


@dataclass
class RamaCase(Nodo):
    nombre_variable: str = '_no_set'
    tipo: str = '_no_set'
    cuerpo: Expresion = None
    cast: str = '_no_type'

    def TIPO(self, ambito):
        self.cast = self.tipo

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_branch\n'
        resultado += f'{(n+2)*" "}{self.nombre_variable}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Switch(Nodo):
    expr: Expresion = None
    casos: List[RamaCase] = field(default_factory=list)

    def TIPO(self, ambito):
        # TODO - El tipo del switch varia en funcion de la rama que se tome al evaluar la expr
        nuevoAmbito = deepcopy(ambito)
        self.expr.TIPO(nuevoAmbito)
        # TODO - Si el tipo de expr es void lanzo excepcion
        '''
        TODO
        Each branch of a case is type checked in an environment where variable xi has type Ti. 
        The type of the entire case is the join of the types of its branches. 
        The variables declared on each branch of a case must all have distinct types.
        TODO - Como junto los tipos?
        '''
        for caso in self.casos:
            caso.TIPO(nuevoAmbito)
            self.cast = caso.cast # TODO

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_typcase\n'
        resultado += self.expr.str(n+2)
        resultado += ''.join([c.str(n+2) for c in self.casos])
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

@dataclass
class Nueva(Nodo):
    tipo: str = '_no_set'
    cast: str = '_no_type'

    def TIPO(self, ambito):
        self.cast = self.tipo

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_new\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado



@dataclass
class OperacionBinaria(Expresion):
    izquierda: Expresion = None
    derecha: Expresion = None

    def TIPO(self, ambito):
        self.izquierda.TIPO(ambito)
        self.derecha.TIPO(ambito)
        if self.izquierda.cast == self.derecha.cast:
            self.cast = self.izquierda.cast
        else:
            raise CodeError(f"Left and right are not same type: {self.izquierda} operator {self.derecha}")


@dataclass
class Suma(OperacionBinaria):
    operando: str = '+'

    def TIPO(self, ambito):
        self.izquierda.TIPO(ambito)
        self.derecha.TIPO(ambito)
        # TODO - Cambiar como estan hechos los condicionales
        if self.izquierda.cast == "Int": 
            if self.derecha.cast == "Int": 
                self.cast = "Int"
            else:
                raise CodeError(f"No se pueden sumar {self.izquierda.cast} + {self.derecha.cast}")
                #self.cast = "Object"
        else:
                self.cast = "Object"
        
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_plus\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Resta(OperacionBinaria):
    operando: str = '-'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_sub\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Multiplicacion(OperacionBinaria):
    operando: str = '*'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_mul\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado



@dataclass
class Division(OperacionBinaria):
    operando: str = '/'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_divide\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Menor(OperacionBinaria):
    operando: str = '<'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_lt\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

@dataclass
class LeIgual(OperacionBinaria):
    operando: str = '<='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_leq\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Igual(OperacionBinaria):
    operando: str = '='

    def TIPO(self, ambito):
        self.izquierda.TIPO(ambito)
        self.derecha.TIPO(ambito)
        if self.izquierda.cast != self.derecha.cast:
            raise CodeError(f"No se pueden comparar tipos {self.izquierda.cast} y {self.derecha.cast}")
        self.cast = "Bool"

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_eq\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado



@dataclass
class Neg(Expresion):
    expr: Expresion = None
    operador: str = '~'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_neg\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado



@dataclass
class Not(Expresion):
    expr: Expresion = None
    operador: str = 'NOT'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_comp\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class EsNulo(Expresion):
    expr: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_isvoid\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado




@dataclass
class Objeto(Expresion):
    nombre: str = '_no_set'

    def TIPO(self, ambito):
        self.cast = ambito.tipoVar(self.nombre) #"Object"

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_object\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class NoExpr(Expresion):
    nombre: str = ''

    def TIPO(self, ambito):
        self.cast = "_no_type"

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_no_expr\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Entero(Expresion):
    valor: int = 0

    def TIPO(self, ambito):
        # Los atributos del padre
        self.cast = "Int" 

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_int\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class String(Expresion):
    valor: str = '_no_set'

    def TIPO(self, ambito):
        # Los atributos del padre
        self.cast = "String"

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_string\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado



@dataclass
class Booleano(Expresion):
    valor: bool = False

    def TIPO(self, ambito):
        # nuevoAmbito = deepcopy(ambito)
        self.cast = "Bool"
        

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_bool\n'
        resultado += f'{(n+2)*" "}{1 if self.valor else 0}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

@dataclass
class IterableNodo(Nodo):
    secuencia: List = field(default_factory=List)

'''
Inicio del ...
a. 2 strings, nombres de clases (1 es subtipo de otra)
b. nombre del metodo + nombre clase: devolver el nombre de los argumentos con su tipo y el tipo de retorno
c. Poder añadir clases al arbol (diciendo quien es su padre)
d. Añadir métodos a una clase
e. Decir nombre de una variable y que devuelva su tipo
'''
class Ambito():

    def __init__(self):
        self.claseActual = "Object"
        self.palabrasReservadas = set(["self"])
        self.herencia = defaultdict(lambda: "Object") # clase: padre
        self.herencia['Int']
        self.herencia['String']
        self.herencia['Bool']
        
        '''
        Object
        abort() : Object
        type_name() : String
        copy() : SELF_TYPE

        String 
        length() : Int
        concat(s : String) : String
        substr(i : Int, l : Int) : String

        IO
        out_string(x : String) : SELF_TYPE
        out_int(x : Int) : SELF_TYPE
        in_string() : String
        in_int() : Int

        '''
        self.metodos = {
            ("Object", "abort"): ["Object"],
            ("Object", "type_name"): ["String"],
            ("Object", "copy"): ["SELF_TYPE"],

            ("String", "length"): ["Int"],
            ("String", "concat"): ["String", "String"],
            ("String", "substr"): ["Int", "Int", "String"],

            ("IO", "out_string"): ["String", "SELF_TYPE"],
            ("IO", "out_int"): ["Int", "SELF_TYPE"],
            ("IO", "in_string"): ["String"],
            ("IO", "in_int"): ["Int"],
        } #(clase, metodo): [argumentos, tipo_retorno]
        
        self.variables = {} # argumento: tipo
        self.variablesClase = defaultdict(lambda: set())
    
    def addClase(self, clase, padre): 
        if clase in self.herencia:
            raise CodeError(f"No se puede sobreescribir la clase {clase}")
        self.herencia[clase] =  padre

    def setClaseActual(self, clase): 
        self.claseActual = clase

    '''
    Crea estructura de variables para las clases que no son la actual por si
    hay que realizar herencia.
    var: (nombre, tipo)
    '''
    def addVarHerencia(self, var, clase):
        self.variablesClase[clase].add(var)

    '''
    Comprueba si una clase hereda de otra
    '''
    def esPadre(self, padre, clase):
        claseOriginal = clase
        while self.padre(clase) != padre: #
            cp = self.padre(clase)
            if clase == cp:
                return False
            clase = cp
        return True

    def padre(self, clase): 
        return self.herencia[clase]

    def mudarVariablesPadre(self, padre): 
        # TODO - Añadir nombres (y tipo) a la estructura de herencia
        for nvar, tvar in self.variablesClase[padre]:
            self.variables[nvar] = tvar
        pass
    

    '''
    Añade un método nuevo
    TODO - Hay que añadir los parámetros a las variables??
        metodo: nombre del metodo a añadir
        clase: nombre de la clase a añadir
        argumentos: [(name : type), (n2 : t2), ..., tipoRetorno]
    '''
    def addMetodo(self, metodo, clase, argumentos): 
        self.metodos[(clase, metodo)] = argumentos

    '''
    returns: argumentos del metodo indicado
    '''
    def argumentos(self, clase, metodo): 
        claseOriginal = clase
        while (clase, metodo) not in self.metodos: #
            cp = self.padre(clase)
            if clase == cp:
                raise CodeError(f"Método no encontrado: {claseOriginal}, {metodo}") 
            clase = cp
        tipo = self.metodos[(clase, metodo)][-1]
        if tipo == "SELF_TYPE":
            tipo = claseOriginal
        if tipo == ('map', 'String'):
            print(2)
        return self.metodos[(clase, metodo)][:-1]+[tipo]

    def addVar(self, nombreVar, tipo, clase = None):
        # Palabra reservada
        if nombreVar in self.palabrasReservadas:
            raise CodeError(f"Nombre de variable no permitido: {nombreVar}")
        if clase:
            # Nombre de variable ya registrado en herencia
            clase = self.padre(clase)
            found = False
            while not found and clase != "Object":
                for v, _ in self.variablesClase[clase]: # Busco si el padre tiene una variable con el mismo nombre
                    if v == nombreVar: found = True; break
                clase = self.padre(clase)
            if found: 
                raise CodeError(f"Variable ya definida {nombreVar}, {clase}")
        
        # Correcto
        self.variables[nombreVar] = tipo

    def tipoVar(self, nombreVar): 
        if nombreVar == "self": return self.claseActual

        if nombreVar not in self.variables:
            raise CodeError(f"Variable '{nombreVar}' no definida")
        
        return self.variables[nombreVar]


class Programa(IterableNodo):

    def TIPO(self):
        ambito = Ambito()
        for clase in self.secuencia: # Guardar todas las clases antes de entrar 
            ambito.addClase(clase.nombre, clase.padre)
            for caracteristica in clase.caracteristicas:
                if isinstance(caracteristica, Metodo): # TODO añadir bien la caracteristica
                    ambito.addMetodo(caracteristica.nombre, clase.nombre, [formal.tipo for formal in caracteristica.formales] + [caracteristica.tipo]) #[(formal.nombre_variable, formal.tipo) for formal in caracteristica.formales])
                else: # Atributo (Variable)
                    caracteristica.TIPO(ambito)
                    ambito.addVarHerencia((caracteristica.nombre, caracteristica.cast), clase.nombre) # Para después la herencia
        for clase in self.secuencia:
            clase.TIPO(ambito)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{" "*n}_program\n'
        resultado += ''.join([c.str(n+2) for c in self.secuencia])
        return resultado

@dataclass
class Caracteristica(Nodo):
    nombre: str = '_no_set'
    tipo: str = '_no_set'
    cuerpo: Expresion = None

    def TIPO(self, ambito): 
        self.cuerpo.TIPO(ambito)
        self.cast = self.tipo 

@dataclass
class Clase(Nodo):
    nombre: str = '_no_set'
    padre: str = '_no_set'
    nombre_fichero: str = '_no_set'
    caracteristicas: List[Caracteristica] = field(default_factory=list)

    def TIPO(self, ambito):
        nuevoAmbito = deepcopy(ambito)
        nuevoAmbito.setClaseActual(self.nombre)
        if self.padre != "Object":
            nuevoAmbito.mudarVariablesPadre(self.padre)
        for caracteristica in self.caracteristicas:
            if isinstance(caracteristica, Metodo):
                # nuevoAmbito.addMetodo(caracteristica.nombre, self.nombre,[(formal.nombre_variable, formal.tipo) for formal in caracteristica.formales]+["NOTYPE"]) 
                caracteristica.TIPO(nuevoAmbito)
            else: # Atributo
                nuevoAmbito.addVar(caracteristica.nombre, caracteristica.tipo, self.nombre)
                caracteristica.TIPO(nuevoAmbito)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_class\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.padre}\n'
        resultado += f'{(n+2)*" "}"{self.nombre_fichero}"\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.caracteristicas])
        resultado += '\n'
        resultado += f'{(n+2)*" "})\n'
        return resultado

@dataclass
class Metodo(Caracteristica):
    formales: List[Formal] = field(default_factory=list)

    def TIPO(self, ambito:Ambito):
        nuevoAmbito = deepcopy(ambito)
        for formal in self.formales:
            nuevoAmbito.addVar(formal.nombre_variable, formal.tipo)
        self.cuerpo.TIPO(nuevoAmbito)

        # self.cast = self.formales[-1].cast

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_method\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += ''.join([c.str(n+2) for c in self.formales])
        resultado += f'{(n + 2) * " "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)

        return resultado


class Atributo(Caracteristica):

    def TIPO(self, ambito: Ambito):
        self.cuerpo.TIPO(ambito)
        sc = self.cuerpo.cast
        if sc != "_no_type":
            # si el tipo no es igual al del cuerpo 
            # o
            # el tipo no es padre del cuerpo
            if self.tipo != sc and not ambito.esPadre(self.tipo, sc):
                raise CodeError(f"Tipo definido no es igual al del valor: {self.tipo} != {sc}")
        
        self.cast = self.tipo

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_attr\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado
