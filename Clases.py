# coding: utf-8
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List

errores_tipo = []

class CodeError(Exception):
    def __init__(self, message, nlinea = None):
        self.message =  message
        self.nlinea = nlinea
        m = (f"(line {nlinea}) " if nlinea else "") + message
        super().__init__(m)

@dataclass
class Nodo:
    linea: int = 0

    def VALOR(self):
        def valor(): return None

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

    def VALOR(self):
        def valor(): return None
        return valor


@dataclass
class Asignacion(Expresion):
    nombre: str = '_no_set'
    cuerpo: Expresion = None

    def TIPO(self, ambito):
        self.cuerpo.TIPO(ambito)
        sc = self.cuerpo.cast
        t = ambito.tipoVar(self.nombre)
        if self.nombre == "self":
            raise CodeError("No se puede asignar self", self.linea)
        if not t:
            raise CodeError(f"Variable '{self.nombre}' no definida", self.linea)
        if t != sc and not ambito.esPadre(t, sc):
            raise CodeError(f"Tipo de asignación no coincide con el designado para la variable: {t} != {sc}", self.linea)
            # cells <- (new CellularAutomaton).init("         X         ");
        self.cast = t
        self.ambito = ambito # TODO - Poner en todas las clases
        from main import PRACTICA
        if PRACTICA == "04":
            self.VALOR()

    def VALOR(self):
        valor = self.cuerpo.VALOR()
        self.ambito.setValVar(self.nombre, valor)

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

    '''
    Provides a way of accessing methods of parent classes that have been hidden by
    redefinitions in child classes. 
    Instead of using the class of the leftmost expression to determine the method, 
    the method of the class explicitly specified is used. For example, 
    e@B.f() invokes the method f in class B on the object that is the value of e. 
    For this form of dispatch, 
    the static type to the left of “@”must conform to the type specified to the right of “@”.

    self.cuerpo @ self.clase . self.nombre_metodo ( self.argumentos )
    '''
    def TIPO(self, ambito):
        # TODO - No entiendo la sintaxis del metodo estatico.
        self.cuerpo.TIPO(ambito)
        if self.cuerpo.cast != self.clase:
            if not ambito.esPadre(self.clase, self.cuerpo.cast):
                raise CodeError(f"El tipo de dispatch no coincide: {self.cuerpo.cast} != {self.clase}", self.linea)
        argsFirma = ambito.argumentos(self.clase, self.nombre_metodo)
        if not argsFirma:
            raise CodeError(f"Método no encontrado: {self.clase}, {self.nombre_metodo}", self.linea)
        tipo = argsFirma[-1]
        args = argsFirma[:-1]
 
        for arg, argF in zip(self.argumentos, args): # Compruebo que el tipo de los argumentos pasados sea el correcto
            arg.TIPO(ambito)
            # Ambito().esPadre()
            if arg.cast != argF and not ambito.esPadre(padre = argF, clase = arg.cast):
                raise CodeError(f"El tipo del argumento no coincide con el esperado: {arg.cast} != {argF}", self.linea)
        self.cast = tipo

        '''
        ("IO", "out_string"): ["String", "SELF_TYPE"],
        ("IO", "out_int"): ["Int", "SELF_TYPE"],
        '''
        if self.nombre_metodo == "out_string": # TODO
            print(ambito.getVar(self.argumentos.nombre))
        elif self.nombre_metodo == "out_int":
            print(ambito.getVar(self.argumentos.nombre))

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_static_dispatch\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n+2)*" "}{self.clase}\n'
        resultado += f'{(n+2)*" "}{self.nombre_metodo}\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.argumentos])
        resultado += f'{(n+2)*" "})\n'
        # resultado += f'{(n)*" "}: _no_type\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
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
        if not argsFirma:
            raise CodeError(f"Método estatico no encontrado: {self.nombre_metodo}", self.linea)
    
        tipo = argsFirma[-1]
        argsCorrectos = argsFirma[:-1]

        for arg, argCorrecto in zip(self.argumentos, argsCorrectos): # Compruebo que el tipo de los argumentos pasados sea el correcto
            arg.TIPO(ambito)
            if arg.cast != argCorrecto and not ambito.esPadre(argCorrecto, arg.cast) and arg: # TODO - Tener en cuenta herencia
                raise CodeError(f"El tipo del argumento no coincide con el esperado: {arg.cast} != {argCorrecto}", self.linea)
        
        if tipo == "SELF_TYPE":
            if self.cuerpo.cast != ambito.claseActual:
                tipo = self.cuerpo.cast
                # self.tp = self.cuerpo.cast
            else:
                # self.tp = "SELF_TYPE"
                tipo = ambito.claseActual
        else: self.tp = tipo
        self.cast = tipo
        self.ambito = ambito
        # from main import PRACTICA
        # if PRACTICA == "04":
        #     self.VALOR()
        # TODO - Faltan muchos métodos

    def VALOR(self):
        # TODO - Llamar a método con cuerpo correcto (hay que guardarlo antes)
        '''
        ("IO", "out_string"): ["String", "SELF_TYPE"],
        ("IO", "out_int"): ["Int", "SELF_TYPE"],
        '''
        if self.nombre_metodo == "out_string": # TODO
            a = self.argumentos[0]
            # if isinstance(a, String) or isinstance(a, Entero) or isinstance(a, Booleano):
            valor = a.VALOR()()
            if valor == '"\\n"': print()
            else:
                if isinstance(valor, str):
                    valor = valor.replace('"', "")
                print(valor, end='')
            
        elif self.nombre_metodo == "out_int":
            print(self.ambito.getVar(self.argumentos[0].nombre)(), end=''   )
        elif self.nombre_metodo == "abort":
            #exit(0) # TODO - Solo parar la ejecución actual
            raise CodeError("Abortado", self.linea)

        # ("Object", "type_name"): ["String"],
        elif self.nombre_metodo == "type_name":
            # def valor(): return self.ambito.getVar(self.cuerpo.nombre)[1]
            # return valor # Calcular un metodo
            return self.ambito.getVar(self.cuerpo.nombre)[1]

        elif self.nombre_metodo == "copy":
            # def valor(): return self.ambito.getVar(self.cuerpo.nombre)[1]
            # return valor # Calcular un metodo
            # return self.ambito.getVar(self.cuerpo.nombre)[1]
            return self.cuerpo.VALOR()

    def str(self, n):
        # c = self.cast if self.cast != self.ambito.claseActual else "SELF_TYPE"
        # c = self.tp
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

    def TIPO(self, ambito):
        self.condicion.TIPO(ambito)
        if self.condicion.cast != "Bool":
            raise CodeError(f'Condicion del condicional debe ser Bool no "{self.condicion.cast}"', self.linea)
        
        # TODO - No calculo los tipos para que no se rompa (llamar a abort (en llamadaMetodo.TIPO esta el .VALOR))
        self.verdadero.TIPO(ambito)
        self.falso.TIPO(ambito)
        tv, tf = self.verdadero.cast, self.falso.cast
        if self.condicion == "true":
            self.cast = tv
        elif self.condicion == "false":
            self.cast = tf
        elif tv != tf:
            self.cast = "Object" #[tv, tf] # TODO
        else:
            self.cast = tv
            # raise CodeError(f'Condicion de la rama falsa y verdadera deben coincid condicional debe ser Bool no "{self.condicion.cast}"', self.linea)
        self.ambito = ambito
        from main import PRACTICA
        if PRACTICA == "04":
            self.VALOR()

    def VALOR(self): # TODO
        if self.condicion.VALOR()() == "True":
            return self.verdadero.VALOR()
        else:
            return self.falso.VALOR()
    
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
            raise CodeError("Condición del bucle while no es un Bool.", self.linea)
        self.cuerpo.TIPO(ambito)
        # self.cast = self.cuerpo.cast
        self.cast = "Object"

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
        self.ambito = nuevoAmbito
        # TODO - Comprobar si la asignacion es correcta
        nuevoAmbito.addVar(self.nombre,self.tipo)
        
        if self.inicializacion and not isinstance(self.inicializacion, NoExpr):
            self.inicializacion.TIPO(nuevoAmbito)
            if self.tipo != self.inicializacion.cast and not ambito.esPadre(self.tipo, self.inicializacion.cast):
                raise CodeError(f"Tipo de asignacion en Let no coincide con el tipo especificado: {self.inicializacion.cast} != {self.tipo}")
            from main import PRACTICA
            if PRACTICA == "04":
                self.VALOR()
        
        # Continuo con el cuerpo del let
        self.cuerpo.TIPO(nuevoAmbito)
        from main import PRACTICA
        if PRACTICA == "04":
            self.cuerpo.VALOR()
        self.cast = self.cuerpo.cast

    def VALOR(self): # TODO 
        self.ambito.setValVar(self.nombre, self.inicializacion.VALOR())

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
        self.c = "SELF_TYPE" if self.cast == ambito.claseActual else self.cast

    def VALOR(self):
        for e in self.expresiones:
            # try:
            e.VALOR()
            # except Exception as ex: print(ex)

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
        # Ambito().addVar()
        # TODO - Cuerpo.TIPO
        ambito.addVar(self.nombre_variable, self.tipo)
        self.cuerpo.TIPO(ambito)
        self.cast = self.tipo
        # pass

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_branch\n'
        resultado += f'{(n+2)*" "}{self.nombre_variable}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        # resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Switch(Nodo):
    expr: Expresion = None
    casos: List[RamaCase] = field(default_factory=list)
    cast: str = "_no_type"

    def TIPO(self, ambito):
        # TODO - El tipo del switch varia en funcion de la rama que se tome al evaluar la expr
        nuevoAmbito = deepcopy(ambito)
        self.expr.TIPO(nuevoAmbito)
        tipoEsperado = self.expr.cast
        # TODO - Si el tipo de expr es void lanzo excepcion
        '''
        Each branch of a case is type checked in an environment where variable xi has type Ti. 
        The type of the entire case is the join of the types of its branches. 
        The variables declared on each branch of a case must all have distinct types.
        TODO - Como junto los tipos?
        '''
        tipo = "Object"
        tipos = []
        tiposEncontrados = set()
        for caso in self.casos:
            caso.TIPO(nuevoAmbito)
            tipo = caso.cast
            tipos.append(tipo)
            if tipo in tiposEncontrados:
                raise CodeError(f"Tipo repetido en Case: {tipo}", self.linea)
            tiposEncontrados.add(tipo)
            # self.cast = tipo # TODO - Esto no es así, es la unión de los tipos (el padre de todos)
        
        # for tipoE in tiposEncontrados:
        #     if tipoE == tipoEsperado or nuevoAmbito.esPadre(tipoEsperado, tipoE):
        #         tipo = tipoE
                # break
        tipo = tipoEsperado
        self.cast = tipo

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
        if self.tipo == "SELF_TYPE":
            self.cast = ambito.claseActual
        else:
            self.cast = self.tipo

    def VALOR(self):
        def valor(): return None # TODO - Que valor tiene una nueva clase?
        return valor

    def str(self, n):
        c = self.cast if self.tipo != "SELF_TYPE" else 'SELF_TYPE'
        resultado = super().str(n)
        resultado += f'{(n)*" "}_new\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += f'{(n)*" "}: {c}\n'
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
            raise CodeError(f"Left and right are not same type: {self.izquierda} operator {self.derecha}", self.linea)


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
                raise CodeError(f"No se pueden sumar {self.izquierda.cast} + {self.derecha.cast}", self.linea)
                #self.cast = "Object"
        else:
                self.cast = "Object"
        # self.ambito = ambito

    def VALOR(self):
        return self.izquierda.VALOR() + self.derecha.VALOR()
        
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

    def TIPO(self, ambito):
        self.izquierda.TIPO(ambito)
        self.derecha.TIPO(ambito)
        if self.izquierda.cast != "Int" or self.derecha.cast != "Int": 
            raise CodeError(f"No se pueden comparar (menos que) {self.izquierda.cast} < {self.derecha.cast}", self.linea)
            
        self.cast = "Bool"
        

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

    def TIPO(self, ambito):
        self.izquierda.TIPO(ambito)
        self.derecha.TIPO(ambito)
        if self.izquierda.cast != "Int" or self.derecha.cast != "Int": 
            raise CodeError(f"No se pueden comparar (menor o igual que) {self.izquierda.cast} < {self.derecha.cast}", self.linea)
            
        self.cast = "Bool"

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
        # Si el derecho o el izquierdo es un tipo primitivo y los 2 tipos no son iguales
        tizq, tdrch = self.izquierda.cast, self.derecha.cast

        if ambito.tipoPrimitivo(tizq) or ambito.tipoPrimitivo(tdrch):
            if tizq != tdrch:
                raise CodeError(f"No se pueden comparar tipos {self.izquierda.cast} y {self.derecha.cast}", self.linea)
        self.cast = "Bool"
        self.ambito = ambito

    def VALOR(self):
        tizq, tdrch = self.izquierda.VALOR(), self.derecha.VALOR()
        def valorV(): return "True"
        def valorF(): return "False"
        if tizq() != tdrch():
            return valorF
        return valorV
            # raise CodeError(f"No se pueden comparar tipos {self.izquierda.cast} y {self.derecha.cast}", self.linea)
        if self.izquierda == self.derecha:
            return "True"
        else: return "False"

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

    def TIPO(self, ambito):
        self.expr.TIPO(ambito)
        if self.expr.cast != "Int":
            raise CodeError(f"No se puede invertir el signo de un tipo no Int: {self.expr.cast}", self.linea)
        self.cast = "Int"

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

    def TIPO(self, ambito):
        self.expr.TIPO(ambito)
        if self.expr.cast != "Bool":
            raise CodeError(f"No se puede negar un tipo no Bool: {self.expr.cast}", self.linea)
        self.cast = "Bool"

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_comp\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class EsNulo(Expresion):
    expr: Expresion = None

    def TIPO(self, ambito):
        self.expr.TIPO(ambito)
        self.cast = "Bool"
        if isinstance(self.expr, NoExpr): return 

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
        
        
        tipo = ambito.tipoVar(self.nombre) # TODO - Falta Herencia
        if not tipo:
            raise CodeError(f"Variable '{self.nombre}' no definida", self.linea)
        self.cast = tipo
        self.ambito = ambito

    def VALOR(self):
        tipo, valor = self.ambito.getVar(self.nombre)
        # if not valor:
        #     v = self.ambito.defaultVal(tipo)
        #     def valor(): return v
        # else:
        return valor
        # raise CodeError("Valor de Objeto")

    def str(self, n):
        # if self.cast != "no_type":
        c = 'SELF_TYPE' if self.nombre == "self" and self.cast != "_no_type" else self.cast
        resultado = super().str(n)
        resultado += f'{(n)*" "}_object\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n)*" "}: {c}\n'
        return resultado


@dataclass
class NoExpr(Expresion):
    nombre: str = ''

    def TIPO(self, ambito):
        self.cast = "_no_type"

    def VALOR(self):
        def valor(): return None
        return None

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

    def VALOR(self): # TODO quiza no valor entero
        def valor(): return self.valor
        return valor 

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

    def VALOR(self):
        def valor(): return self.valor
        return valor

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
        
    def VALOR(self):
        def valor(): return self.valor
        return valor

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
        self.herencia['Object'] # TODO - CUIDADO
        self.herencia['Int']
        self.herencia['String']
        self.herencia['Bool']
        self.herencia['IO']

        self.tiposPrimitivos = set(['Int', 'String', 'Bool', 'Object']) #'IO']) # TODO
        self.defaultValues = defaultdict(lambda:None)
        self.defaultValues['Int'] = 0
        self.defaultValues['String'] = '""'
        self.defaultValues['Bool'] = False

        '''
        Tipos Primitivos
        ----------------
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
        
        self.variables = {} # argumento: tipo, valor
        self.variablesClase = defaultdict(lambda: set())
        self.metodosClase = defaultdict(lambda: [])
    
    def addClase(self, clase, padre, linea = None): 
        if clase in self.herencia:
            raise CodeError(f"No se puede sobreescribir la clase {clase}", linea)
        self.herencia[clase] =  padre

    def existeClase(self, clase):
        return clase in self.herencia

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
    Determina si un nombre de variable existe para una clase padre de la actual.
        nombreVar: Nombre de variable a analizar

    returns {False: no existe, True: Si existe}
    '''
    def varHerencia(self, nombreVar):
        clase = self.claseActual
        while clase != "Object":
        #    if nombreVar in self.variablesClase[self.padre(clase)]:
            if any(nombreVar == v for v, t in list(self.variablesClase[self.padre(clase)])):
               return True
            clase = self.padre(clase)
        
        return False

    '''
    Comprueba si una clase hereda de otra
        padre: Clase super
        clase: clase a analizar
    '''
    def esPadre(self, padre, clase):
        claseOriginal = clase
        while self.padre(clase) != padre: #
            cp = self.padre(clase)
            if clase == cp:
                return False
            clase = cp
        return True

    '''
    Devuelve el padre inmediato de una clase dada
        clase: Clase de la que conseguir el padre
    '''
    def padre(self, clase): 
        try:
            return self.herencia[clase]
        except: pass # TODO - Si pasan una lista de clases no hay comportamiento definido

    # TODO - También habría que copiar métodos del padre
    def mudarVariablesPadre(self, padre): 
        # TODO - Añadir nombres (y tipo) a la estructura de herencia
        nPadre = padre
        while nPadre != "Object":
            for nvar, tvar in self.variablesClase[nPadre]:
                if nvar not in self.variables: # TODO - Cuidado con el orden de sobreescribir en la herencia
                    self.variables[nvar] = (tvar, None)
            nPadre = self.padre(nPadre)
        
    

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
                return None 
            clase = cp
        tipo = self.metodos[(clase, metodo)][-1]
        # if tipo == "SELF_TYPE":
        #     tipo = claseOriginal
    
        return self.metodos[(clase, metodo)][:-1]+[tipo]

    def metodoHerencia(self, metodo):
        clase = self.padre(self.claseActual)
        foundMethod =  []
        while (clase,metodo) not in self.metodos and clase != "Object":
            clase = self.padre(clase)
        if (clase, metodo) in self.metodos:
            foundMethod = self.metodos[(clase, metodo)]
        return foundMethod


    '''
    Añade una variable dada a la lista de variables
        nombreVar: Nombre de la variable
        tipo: tipo de la variable
        valor: valor de la variable, si no se pasa se deja en None para actualizar despues
        
        # Si se desea comprobar si se deberia añadir se deben pasar estos 2 argumentos
            clase: Clase de la que proviene para comprobar si ya existe en algun padre
            linea: para facilitar crear el error
    '''
    def addVar(self, nombreVar, tipo, valor = None, clase = None, linea = None):
        # Palabra reservada
        if nombreVar in self.palabrasReservadas:
            raise CodeError(f"Nombre de variable no permitido: {nombreVar}", linea)
        if clase:
            # Nombre de variable ya registrado en herencia
            clase = self.padre(clase)
            found = False
            while not found and clase != "Object":
                for v, _ in self.variablesClase[clase]: # Busco si el padre tiene una variable con el mismo nombre
                    if v == nombreVar: found = True; break
                clase = self.padre(clase)
            if found: 
                raise CodeError(f"Variable ya definida {nombreVar}, {clase}", linea)
        
        # Correcto
        if valor == None:
            v = self.defaultValues[tipo]
            def valorF(): return v
            self.variables[nombreVar] = (tipo, valorF)
        # else:
        #     self.variables[nombreVar] = (tipo,)

    def setValVar(self, nombreVar, valor):
        if nombreVar in self.variables:
            self.variables[nombreVar] = (self.variables[nombreVar][0], valor)
        else:
            raise CodeError("Variable deberia existir ya, hay un error")


    def getVar(self, nombreVar):
        if nombreVar in self.variables:
            return self.variables[nombreVar]
        else:
            return None

    def tipoVar(self, nombreVar): 
        if nombreVar == "self": return self.claseActual

        if nombreVar not in self.variables:
            return None
        
        return self.variables[nombreVar][0] # TODO - Cambiar addVar para incluir tipo

    def tipoPrimitivo(self, tipo):
        return tipo in self.tiposPrimitivos


class Programa(IterableNodo):

    def TIPO(self):
        ambito = Ambito()
        for clase in self.secuencia: # Guardar todas las clases antes de entrar 
            if ambito.tipoPrimitivo(clase.nombre) or clase.nombre == "SELF_TYPE":
                raise CodeError("No se puede sobreescribir una clase primitiva", clase.linea)

            ambito.addClase(clase.nombre, clase.padre, linea=clase.linea)
            for caracteristica in clase.caracteristicas:
                if isinstance(caracteristica, Metodo): # TODO añadir bien la caracteristica
                    ambito.addMetodo(caracteristica.nombre, clase.nombre, [formal.tipo for formal in caracteristica.formales] + [caracteristica.tipo]) #[(formal.nombre_variable, formal.tipo) for formal in caracteristica.formales])                    
                    for formal in caracteristica.formales:
                        if formal.tipo == "SELF_TYPE": raise CodeError(f"Los parametros formales no pueden tener tipo SELF_TYPE: {formal.nombre_variable} : {formal.tipo}", formal.linea) 
                else: # Atributo (Variable)
                    # caracteristica.TIPO(ambito)
                    ambito.addVarHerencia((caracteristica.nombre, caracteristica.tipo), clase.nombre) # Para después la herencia
        if not ambito.existeClase("Main"):
            raise CodeError("Clase Main no definida")
        for clase in self.secuencia:
            clase.TIPO(ambito)
        self.ambito = ambito

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
            if ambito.tipoPrimitivo(self.padre):
                raise CodeError(f'La clase "{self.nombre}" no puede heredar del tipo primitivo {self.padre}.')
            if self.padre == "SELF_TYPE":
                raise CodeError(f'La clase "{self.nombre}" no puede heredarse a si misma.', self.linea)
            if not nuevoAmbito.existeClase(self.padre):
                raise CodeError(f'La clase padre "{self.padre}" no existe y no puede ser heredada', self.linea)
            nuevoAmbito.mudarVariablesPadre(self.padre)
        for caracteristica in self.caracteristicas:
            if isinstance(caracteristica, Metodo):
                # nuevoAmbito.addMetodo(caracteristica.nombre, self.nombre,[(formal.nombre_variable, formal.tipo) for formal in caracteristica.formales]+["NOTYPE"]) 
                caracteristica.TIPO(nuevoAmbito)
            else: # Atributo
                nuevoAmbito.addVar(caracteristica.nombre, caracteristica.tipo, self.nombre, linea=caracteristica.linea)
                caracteristica.TIPO(nuevoAmbito)
    
    def VALOR(self):
        def valor(): return None
        return valor

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
        nombresVar = set()
        for formal in self.formales:
            if formal.nombre_variable in nombresVar:
                raise CodeError(f'Nombre de parametro "{formal.nombre_variable}" repetido.')
            nombresVar.add(formal.nombre_variable)
            nuevoAmbito.addVar(formal.nombre_variable, formal.tipo)

        # Si es que esta sobrescribiendo el metodo del padre
        mHerencia = ambito.metodoHerencia(self.nombre)
        if mHerencia:
            args = [formal.tipo for formal in self.formales]
            if len(args) != len(mHerencia[:-1]):
                raise CodeError(f"Numero de parametros del hijo no coinciden con los del padre: {len(args)} != {len(mHerencia[:-1])}")
            for arg, argPadre in zip(args, mHerencia[:-1]):
                if arg != argPadre:
                    raise CodeError(f"Los parametros del hijo no coinciden con los del padre: {args} != {mHerencia}") 
        
        self.cuerpo.TIPO(nuevoAmbito)
        tipo = self.tipo
        if self.tipo == "SELF_TYPE": # TODO - No cambiar el tipo o arreglar o no se que
            tipo = ambito.claseActual
        if not ambito.existeClase(tipo):
            raise CodeError(f'El tipo definido en el método {self.nombre} no existe "{self.tipo}"', self.linea)
        if self.cuerpo.cast != tipo and not ambito.esPadre(tipo, self.cuerpo.cast):
            raise CodeError(f"El tipo de retorno del método {self.nombre} no coincide: {self.cuerpo.cast} != {self.tipo}", self.linea)

        self.cast = self.tipo #self.formales[-1].cast

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
        
        if self.cuerpo and not isinstance(self.cuerpo, NoExpr): # Cuando se ha definido un valor para asignarlo al atributo
            self.cuerpo.TIPO(ambito)
            sc = self.cuerpo.cast
            if self.tipo != sc and not ambito.esPadre(self.tipo, sc):
                raise CodeError(f"Tipo definido no es igual al del valor: {self.tipo} != {sc}", self.linea)
           
        if ambito.varHerencia(self.nombre):
            raise CodeError(f"No se puede sobreescribir una variable definida en el padre", self.linea)
        
        ambito.addVar(self.nombre, self.tipo)
        self.cast = self.tipo
        
        self.ambito = ambito
        from main import PRACTICA
        if PRACTICA == "04":
            self.VALOR()

    def VALOR(self):
        self.ambito.setValVar(self.nombre, self.cuerpo.VALOR())

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_attr\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado
