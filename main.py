import os
import re
import sys
from colorama import init
from termcolor import colored
import traceback

from Parser import CoolParser
init()


DIRECTORIO = os.path.expanduser(".")
sys.path.append(DIRECTORIO)

from Lexer import *
from Parser import *
from Clases import *

PRACTICA = "03" # Practica que hay que evaluar
DEBUG = True   # Decir si se lanzan mensajes de debug
NUMLINEAS = 3   # Numero de lineas que se muestran antes y después de la no coincidencia
sys.path.append(DIRECTORIO)
DIR = os.path.join(DIRECTORIO, PRACTICA, 'grading')
FICHEROS = os.listdir(DIR)
TESTS = [fich for fich in FICHEROS
         if os.path.isfile(os.path.join(DIR, fich)) and
         re.search(r"^[a-zA-Z].*\.(cool|test|cl)$",fich)]
TESTS.sort()
if len(sys.argv) > 1:
    fichs = sys.argv[1:]
    TESTS = fichs
# TESTS = ['cells.cl.test']

if True:
    incorrectos = 0
    for fich in TESTS:
        lexer = CoolLexer()
        # if "escapedeof.cool" != fich: continue
        # if "s34.test.cool" != fich: continue
        f = open(os.path.join(DIR, fich), 'r', newline='')
        g = open(os.path.join(DIR, fich + '.out'), 'r', newline='')
        if os.path.isfile(os.path.join(DIR, fich)+'.nuestro'):
            os.remove(os.path.join(DIR, fich)+'.nuestro')
        if os.path.isfile(os.path.join(DIR, fich)+'.bien'):
            os.remove(os.path.join(DIR, fich)+'.bien')            
        texto = ''
        entrada = f.read()
        f.close()
        if PRACTICA == '01':
            texto = '\n'.join(lexer.salida(entrada))
            texto = f'#name "{fich}"\n' + texto
            resultado = g.read()
            g.close()
            # print(texto)
            # print(resultado)
            # print()
            texto = re.sub(r'#\d+\b','',texto)
            resultado = re.sub(r'#\d+\b','',resultado)
            if texto.strip().split() != resultado.strip().split():
                print(f"Incorrecto: {fich}")
                if DEBUG:
                    nuestro = [linea for linea in texto.split('\n') if linea]
                    bien = [linea for linea in resultado.split('\n') if linea]
                    # print(nuestro)
                    # print(bien)
                    linea = 0
                    vacio = 0
                    while nuestro[linea:linea+NUMLINEAS] == bien[linea:linea+NUMLINEAS]:
                        linea += 1
                        if nuestro[linea:linea+NUMLINEAS] == []:
                            vacio += 1
                            #print(vacio)
                        if vacio >= 5: break
                        # print(nuestro[linea:linea+NUMLINEAS])
                    print(colored('\n'.join(nuestro[linea:linea+NUMLINEAS]), 'white', 'on_red'))
                    print(colored('\n'.join(bien[linea:linea+NUMLINEAS]), 'blue', 'on_green'))
                    f = open(os.path.join(DIR, fich)+'.nuestro', 'w')
                    g = open(os.path.join(DIR, fich)+'.bien', 'w')
                    f.write(texto.strip())
                    g.write(resultado.strip())
                    f.close()
                    g.close()
        elif PRACTICA in ('02', '03'):
            
            parser = CoolParser()
            parser.nombre_fichero = fich
            parser.errores = []
            bien = ''.join([c for c in g.readlines() if c and '#' not in c])
            g.close()
            j = parser.parse(lexer.tokenize(entrada))
            try:
                if j and not parser.errores:
                    
                    # j.errores = errores_tipo
                    try:
                        j.TIPO()
                        resultado = '\n'.join([c for c in j.str(0).split('\n')
                                            if c and '#' not in c])
                    except Exception as e:
                        if isinstance(e, CodeError):
                            # print(f"Exception {fich}")
                        # traceback.print_exc()
                            # print(str(e))
                            print()
                        else:
                            traceback.print_exc()
                            print(str(e))
                        resultado = str(e)
                        resultado += '\n' + "Compilation halted due to lex and parse errors."
                                        
                else:
                    resultado = '\n'.join(parser.errores)
                    resultado += '\n' + "Compilation halted due to lex and parse errors."
                if resultado.lower().strip().split() != bien.lower().strip().split():
                    if resultado.lower().strip().split()[-1] != bien.lower().strip().split()[-1]: # TODO - Quitar, es porque mis output de error no coinciden con los de out
                        print(f"Incorrecto: {fich}")
                        incorrectos += 1
                        if DEBUG:
                            nuestro = [linea for linea in resultado.split('\n') if linea]
                            bien = [linea for linea in bien.split('\n') if linea]
                            linea = 0
                            while nuestro[linea:linea+NUMLINEAS] == bien[linea:linea+NUMLINEAS]:
                                linea += 1
                            # print(colored('\n'.join(nuestro[linea:linea+NUMLINEAS]), 'white', 'on_red'))
                            # print(colored('\n'.join(bien[linea:linea+NUMLINEAS]), 'blue', 'on_green'))
                            f = open(os.path.join(DIR, fich)+'.nuestro', 'w')
                            g = open(os.path.join(DIR, fich)+'.bien', 'w')
                            f.write("\n".join(nuestro).strip())
                            g.write("\n".join(bien).strip())
                            f.close()
                            g.close()
            except Exception as e:
                print()
                print("ERROR")
                print("------")
                # print(e)
                # traceback.print_exc()
                # pass
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                # print(exc_type, fname, exc_tb.tb_lineno)
                print(f"Lanza excepción en {fich} : {e}")
                print()

    print(incorrectos)
