from itertools import product # Esta función genera productos cartesianos de iterables
import numpy as np # operaciones matemáticas y manipulación de arreglos
from copy import deepcopy # copias profundas de objetos
from random import choice # elegir aleatoriamente un elemento de una secuencia

class Formula :

    def __init__(self) :
        pass

    def __str__(self) :
        if type(self) == Letra:
            return self.letra
        elif type(self) == Negacion:
            return '-' + str(self.subf)
        elif type(self) == Binario:
            return "(" + str(self.left) + self.conectivo + str(self.right) + ")"

    def letras(self): # Devuelve un conjunto de todas las letras proposicionales presentes en la fórmula.
        if type(self) == Letra:
            return set(self.letra)
        elif type(self) == Negacion:
            return self.subf.letras()
        elif type(self) == Binario:
            return self.left.letras().union(self.right.letras())

    def subforms(self): # Devuelve una lista de todas las subfórmulas presentes en la fórmula.
        if type(self) == Letra:
            return [str(self)]
        elif type(self) == Negacion:
            return list(set([str(self)] + self.subf.subforms()))
        elif type(self) == Binario:
            return list(set([str(self)] + self.left.subforms() + self.right.subforms()))

    def num_conec(self): # Devuelve el número de conectivos presentes en la fórmula.
        if type(self) == Letra:
            return 0
        elif type(self) == Negacion:
            return 1 + self.subf.num_conec()
        elif type(self) == Binario:
            return 1 + self.left.num_conec() + self.right.num_conec()

    def valor(self, I) : # Evalúa la fórmula dada una interpretación I de las letras proposicionales.
        if type(self) == Letra:
            return I[self.letra]
        elif type(self) == Negacion:
            return not self.subf.valor(I)
        elif type(self) == Binario:
            if self.conectivo == 'Y':
                return self.left.valor(I) and self.right.valor(I)
            if self.conectivo == 'O':
                return self.left.valor(I) or self.right.valor(I)
            if self.conectivo == '>':
                return not self.left.valor(I) or self.right.valor(I)
            if self.conectivo == '=':
                return (self.left.valor(I) and self.right.valor(I)) or (not self.left.valor(I) and not self.right.valor(I))

    def SATtabla(self): # Determina si la fórmula es satisfacible utilizando el método de tabla de verdad.
        letras = list(self.letras())
        n = len(letras)
        valores = list(product([True, False], repeat=n))
        for v in valores:
            I = {letras[x]: v[x] for x in range(n)}
            if self.valor(I):
                return I
        return None

    def clasifica_para_tableaux(self): # Clasifica la fórmula para su uso en el método de tableaux.
        if type(self) == Letra:
            return None, 'literal'
        elif type(self) == Negacion:
            if type(self.subf) == Letra:
                return None, 'literal'
            elif type(self.subf) == Negacion:
                return 1, 'alfa'
            elif type(self.subf) == Binario:
                if self.subf.conectivo == 'O':
                    return 3, 'alfa'
                elif self.subf.conectivo == '>':
                    return 4, 'alfa'
                elif self.subf.conectivo == 'Y':
                    return 1, 'beta'
        elif type(self) == Binario:
            if self.conectivo == 'Y':
                return 2, 'alfa'
            elif self.conectivo == 'O':
                return 2, 'beta'
            elif self.conectivo == '>':
                return 3, 'beta'

    def SATtableaux(self): # Determina si la fórmula es satisfacible utilizando el método de tableaux.
        estado = nodos_tableaux([self])
        res = estado.es_hoja()
        if res == 'cerrada':
            return None
        elif res == 'abierta':
            return estado.interp()
        frontera = [estado]
        while len(frontera) > 0:
            estado = frontera.pop(0)
            hijos = estado.expandir()
            for a in hijos:
                if a != None:
                    res = a.es_hoja()
                    if res == 'abierta':
                        return a.interp()
                    elif res == None:
                        frontera.append(a)
        return None

    def ver(self, D): # Visualiza la fórmula utilizando un descriptor D.
        '''
        Visualiza una fórmula A (como string en notación inorder) usando el descriptor D
        '''
        vis = []
        A = str(self)
        for c in A:
            if c == '-':
                vis.append(' no ')
            elif c in ['(', ')']:
                vis.append(c)
            elif c in ['>', 'Y', 'O']:
                vis.append(' ' + c + ' ')
            elif c == '=':
                vis.append(' sii ')
            else:
                try:
                    vis.append(D.escribir(c))
                except:
                    raise("¡Caracter inválido!")
        return ''.join(vis)

    def eliminar_imp(self): # Elimina las implicaciones de la fórmula.
        if type(self) == Letra:
            return self
        elif type(self) == Negacion:
            return Negacion(self.subf.eliminar_imp())
        elif type(self) == Binario:
            if self.conectivo == '>':
                return Binario('O',
                               Negacion(self.left.eliminar_imp()),
                               self.right.eliminar_imp()
                              )
            else:
                return Binario(self.conectivo,
                               self.left.eliminar_imp(),
                               self.right.eliminar_imp()
                              )

    def eliminar_doble_imp(self): # Elimina las dobles implicaciones de la fórmula.
        if type(self) == Letra:
            return self
        elif type(self) == Negacion:
            return Negacion(self.subf.eliminar_doble_imp())
        elif type(self) == Binario:
            if self.conectivo == '=':
                return Binario('Y',
                               Binario('O',
                                   Negacion(self.left.eliminar_doble_imp()),
                                   self.right.eliminar_doble_imp(),
                                  ),
                               Binario('O',
                                   Negacion(self.right.eliminar_doble_imp()),
                                   self.left.eliminar_doble_imp(),
                                  ))
            else:
                return Binario(self.conectivo,
                           self.left.eliminar_doble_imp(),
                           self.right.eliminar_doble_imp()
                          )

    def eliminar_doble_negacion(self): # Elimina las dobles negaciones de la fórmula.
        if type(self) == Letra:
            return self
        elif type(self) == Negacion:
            if type(self.subf) == Negacion:
                return deepcopy(self.subf.subf.eliminar_doble_negacion())
            else:
                return Negacion(self.subf.eliminar_doble_negacion())
        elif type(self) == Binario:
            return Binario(self.conectivo,
                           self.left.eliminar_doble_negacion(),
                           self.right.eliminar_doble_negacion())

    def cambiar_de_morgan_y(self): #  Aplica la ley de De Morgan para el operador "Y".
        if type(self) == Letra:
            return self
        elif type(self) == Negacion:
            if type(self.subf) == Binario:
                if self.subf.conectivo == 'Y':
                    return Binario('O',
                                   Negacion(self.subf.left.cambiar_de_morgan_y()),
                                   Negacion(self.subf.right.cambiar_de_morgan_y())
                                  )
                else:
                    return Negacion(self.subf.cambiar_de_morgan_y())
            else:
                return Negacion(self.subf.cambiar_de_morgan_y())
        elif type(self) == Binario:
            return Binario(self.conectivo,
                           self.left.cambiar_de_morgan_y(),
                           self.right.cambiar_de_morgan_y()
                          )

    def cambiar_de_morgan_o(self): # Aplica la ley de De Morgan para el operador "O".
        if type(self) == Letra:
            return self
        elif type(self) == Negacion:
            if type(self.subf) == Binario:
                if self.subf.conectivo == 'O':
                    return Binario('Y',
                                   Negacion(self.subf.left.cambiar_de_morgan_o()),
                                   Negacion(self.subf.right.cambiar_de_morgan_o())
                                  )
                else:
                    return Negacion(self.subf.cambiar_de_morgan_o())
            else:
                return Negacion(self.subf.cambiar_de_morgan_o())
        elif type(self) == Binario:
            return Binario(self.conectivo,
                           self.left.cambiar_de_morgan_o(),
                           self.right.cambiar_de_morgan_o()
                          )

    def distribuir_o_en_y(self): # Distribuye el operador "O" sobre el operador "Y".
        if type(self) == Letra:
            return self
        elif type(self) == Negacion:
            return Negacion(self.subf.distribuir_o_en_y())
        elif type(self) == Binario:
            if self.conectivo == 'O':
                # print('O')
                if type(self.right) == Binario:
                    # print('right binario')
                    if self.right.conectivo == 'Y': # B O (C Y D)
                        # print('right Y')
                        B = self.left.distribuir_o_en_y()
                        C = self.right.left.distribuir_o_en_y()
                        D = self.right.right.distribuir_o_en_y()
                        return Binario('Y',
                                       Binario('O', B, C),
                                       Binario('O', B, D)
                                      )
                if type(self.left) == Binario:
                    # print('left binario')
                    if self.left.conectivo == 'Y': # (B Y C) O D
                        # print('left Y')
                        B = self.left.left.distribuir_o_en_y()
                        C = self.left.right.distribuir_o_en_y()
                        D = self.right.distribuir_o_en_y()
                        return Binario('Y',
                                       Binario('O', B, D),
                                       Binario('O', C, D)
                                      )
        return Binario(self.conectivo,
                       self.left.distribuir_o_en_y(),
                       self.right.distribuir_o_en_y()
                      )

    def fnc(self): # Convierte la fórmula en Forma Normal Conjuntiva
        A = self.eliminar_doble_imp()
        A = A.eliminar_imp()
        A = A.eliminar_doble_negacion()
        A = A.cambiar_de_morgan_y()
        A = A.cambiar_de_morgan_o()
        A = A.eliminar_doble_negacion()
        aux = A.distribuir_o_en_y()
        while str(A) != str(aux):
            A = deepcopy(aux)
            aux = A.distribuir_o_en_y()
        return aux

class Letra(Formula) : #  Toma un parámetro letra que representa el símbolo de una letra proposicional y lo asigna al atributo self.letra
    def __init__ (self, letra:str) :
        self.letra = letra

class Negacion(Formula) : # Toma un parámetro subf que representa una subfórmula y lo asigna al atributo self.subf
    def __init__(self, subf:Formula) :
        self.subf = subf

class Binario(Formula) : # representa la subfórmula derecha. Verifica que el operador binario sea válido y luego asigna los valores a los atributos 
    def __init__(self, conectivo:str, left:Formula, right:Formula) :
        assert(conectivo in ['Y','O','>','='])
        self.conectivo = conectivo
        self.left = left
        self.right = right

def inorder_to_tree(cadena:str): # toma una cadena de entrada cadena que representa una fórmula lógica en notación inorder y la convierte en un árbol de sintaxis abstracta
    conectivos = ['Y', 'O', '>', '=']
    if len(cadena) == 1:
        return Letra(cadena)
    elif cadena[0] == '-':
        return Negacion(inorder_to_tree(cadena[1:]))
    elif cadena[0] == "(":
        counter = 0 #Contador de parentesis
        for i in range(1, len(cadena)):
            if cadena[i] == "(":
                counter += 1
            elif cadena[i] == ")":
                counter -=1
            elif cadena[i] in conectivos and counter == 0:
                return Binario(cadena[i], inorder_to_tree(cadena[1:i]),inorder_to_tree(cadena[i + 1:-1]))
    else:
        raise Exception('¡Cadena inválida!')

class Descriptor :

    '''
    Codifica un descriptor de N argumentos mediante un solo caracter
    Input:  args_lista, lista con el total de opciones para cada
                     argumento del descriptor
            chrInit, entero que determina el comienzo de la codificación chr()
    Output: str de longitud 1
    '''

    def __init__ (self,args_lista,chrInit=256) :
        self.args_lista = args_lista
        assert(len(args_lista) > 0), "Debe haber por lo menos un argumento"
        self.chrInit = chrInit
        self.rango = [chrInit, chrInit + np.prod(self.args_lista)]

    def check_lista_valores(self,lista_valores) : # Verifica si los valores en la lista dada son válidos para el descriptor actual.
        for i, v in enumerate(lista_valores) :
            assert(v >= 0), "Valores deben ser no negativos"
            assert(v < self.args_lista[i]), f"Valor debe ser menor o igual a {self.args_lista[i]}"

    def codifica(self,lista_valores) : # Codifica una lista de valores en un solo número.
        self.check_lista_valores(lista_valores)
        cod = lista_valores[0]
        n_columnas = 1
        for i in range(0, len(lista_valores) - 1) :
            n_columnas = n_columnas * self.args_lista[i]
            cod = n_columnas * lista_valores[i+1] + cod
        return cod

    def decodifica(self,n) : # Decodifica un número codificado en una lista de valores.


        decods = []
        if len(self.args_lista) > 1:
            for i in range(0, len(self.args_lista) - 1) :
                n_columnas = np.prod(self.args_lista[:-(i+1)])
                decods.insert(0, int(n / n_columnas))
                n = n % n_columnas
        decods.insert(0, n % self.args_lista[0])
        return decods

    def ravel(self,lista_valores) : # Codifica una lista de valores en un solo carác
        codigo = self.codifica(lista_valores)
        return chr(self.chrInit+codigo)

    def unravel(self,codigo) : # Decodifica un carácter codificado en una lista de valores.
        n = ord(codigo)-self.chrInit
        return self.decodifica(n)

def Ytoria(lista_forms): # Genera una fórmula lógica que representa la conjunción de todas las fórmulas en la lista dada.
    form = ''
    inicial = True
    for f in lista_forms:
        if inicial:
            form = f
            inicial = False
        else:
            form = '(' + form + 'Y' + f + ')'
    return form

def Otoria(lista_forms): # Genera una fórmula lógica que representa la disyunción de todas las fórmulas en la lista dada.
    form = ''
    inicial = True
    for f in lista_forms:
        if inicial:
            form = f
            inicial = False
        else:
            form = '(' + form + 'O' + f + ')'
    return form

class nodos_tableaux:

    def __init__(self, fs):
        clasfs = [(A, str(A), *A.clasifica_para_tableaux()) for A in fs]
        self.alfas = [c for c in clasfs if c[3] == 'alfa']
        self.betas = [c for c in clasfs if c[3] == 'beta']
        self.literales = [c for c in clasfs if c[3] == 'literal']

    def __str__(self):
        cadena = f'Alfas:{[str(c[1]) for c in self.alfas]}\n'
        cadena += f'Betas:{[str(c[1]) for c in self.betas]}\n'
        cadena += f'Literales:{[str(c[1]) for c in self.literales]}'
        return cadena

    def tiene_lit_comp(self): # Verifica si el nodo tiene una contradicción (un literal y su negación).
        lits = [c[1] for c in self.literales]
        l_pos = [l for l in lits if '-' not in l]
        l_negs = [l[1:] for l in lits if '-' in l]
        return len(set(l_pos).intersection(set(l_negs))) > 0

    def es_hoja(self): # Determina si el nodo es una hoja cerrada, una hoja abierta o no es hoja.
        if self.tiene_lit_comp():
            return 'cerrada'
        elif ((len(self.alfas) == 0) and (len(self.betas) == 0)):
            return 'abierta'
        else:
            return None

    def interp(self): # Devuelve una interpretación válida para las fórmulas en el nodo.
        I = {}
        for lit in self.literales:
            l = lit[1]
            if '-' not in l:
                I[l] = True
            else:
                I[l[1:]] = False
        return I

    def expandir(self): # Expande el nodo, aplicando las reglas del método de tableau para generar nuevos nodos.
        '''Escoge última alfa, si no última beta, si no None'''
        f_alfas = deepcopy(self.alfas)
        f_betas = deepcopy(self.betas)
        f_literales = deepcopy(self.literales)
        if len(self.alfas) > 0:
            f, s, num_regla, cl = f_alfas.pop(0)
            if num_regla == 1:
                formulas = [f.subf.subf]
            elif num_regla == 2:
                formulas = [f.left, f.right]
            elif num_regla == 3:
                formulas = [Negacion(f.subf.left), Negacion(f.subf.right)]
            elif num_regla == 4:
                formulas = [f.subf.left, Negacion(f.subf.right)]
            for nueva_f in formulas:
                clasf = nueva_f.clasifica_para_tableaux()
                if clasf[1]== 'alfa':
                    lista = f_alfas
                elif clasf[1]== 'beta':
                    lista = f_betas
                elif clasf[1]== 'literal':
                    lista = f_literales
                strs = [c[1] for c in lista]
                if str(nueva_f) not in strs:
                    lista.append((nueva_f, str(nueva_f), *clasf))
            nuevo_nodo = nodos_tableaux([])
            nuevo_nodo.alfas = f_alfas
            nuevo_nodo.betas = f_betas
            nuevo_nodo.literales = f_literales
            return [nuevo_nodo, None]
        elif len(self.betas) > 0:
            f, s, num_regla, cl = f_betas.pop(0)
            if num_regla == 1:
                B1 = Negacion(f.subf.left)
                B2 = Negacion(f.subf.right)
            elif num_regla == 2:
                B1 = f.left
                B2 = f.right
            elif num_regla == 3:
                B1 = Negacion(f.left)
                B2 = f.right
            f_alfas2 = deepcopy(f_alfas)
            f_betas2 = deepcopy(f_betas)
            f_literales2 = deepcopy(f_literales)
            clasf = B1.clasifica_para_tableaux()
            if clasf[1]== 'alfa':
                lista = f_alfas
            elif clasf[1]== 'beta':
                lista = f_betas
            elif clasf[1]== 'literal':
                lista = f_literales
            strs = [c[1] for c in lista]
            if str(B1) not in strs:
                lista.append((B1, str(B1), *clasf))
            clasf = B2.clasifica_para_tableaux()
            if clasf[1]== 'alfa':
                lista = f_alfas2
            elif clasf[1]== 'beta':
                lista = f_betas2
            elif clasf[1]== 'literal':
                lista = f_literales2
            strs = [c[1] for c in lista]
            if str(B2) not in strs:
                lista.append((B2, str(B2), *clasf))
            n1 = nodos_tableaux([])
            n1.alfas = f_alfas
            n1.betas = f_betas
            n1.literales = f_literales
            n2 = nodos_tableaux([])
            n2.alfas = f_alfas2
            n2.betas = f_betas2
            n2.literales = f_literales2
            return [n1, n2]
        else:
            return [None, None]

def a_clausal(A): # oma una fórmula A en notación inorder y la convierte en FNC utilizando la transformación de Tseitin. Devuelve una lista de cláusulas.
    # Subrutina de Tseitin para encontrar la FNC de
    # la formula en la pila
    # Input: A (cadena) de la forma
    #                   p=-q
    #                   p=(qYr)
    #                   p=(qOr)
    #                   p=(q>r)
    # Output: B (cadena), equivalente en FNC
    assert(len(A)==4 or len(A)==7), u"Fórmula incorrecta!"
    B = ''
    p = A[0]
    # print('p', p)
    if "-" in A:
        q = A[-1]
        # print('q', q)
        B = "-"+p+"O-"+q+"Y"+p+"O"+q
    elif "Y" in A:
        q = A[3]
        # print('q', q)
        r = A[5]
        # print('r', r)
        B = q+"O-"+p+"Y"+r+"O-"+p+"Y-"+q+"O-"+r+"O"+p
    elif "O" in A:
        q = A[3]
        # print('q', q)
        r = A[5]
        # print('r', r)
        B = "-"+q+"O"+p+"Y-"+r+"O"+p+"Y"+q+"O"+r+"O-"+p
    elif ">" in A:
        q = A[3]
        # print('q', q)
        r = A[5]
        # print('r', r)
        B = q+"O"+p+"Y-"+r+"O"+p+"Y-"+q+"O"+r+"O-"+p
    elif "=" in A:
        q = A[3]
        # print('q', q)
        r = A[5]
        # print('r', r)
        #qO-rO-pY-qOrO-pY-qO-rOpYqOrOp
        B = q+"O"+"-"+r+"O"+"-"+p+"Y"+"-"+q+"O"+r+"O"+"-"+p+"Y"+"-"+q+"O"+"-"+r+"O"+p+"Y"+q+"O"+r+"O"+p
    else:
        print(u'Error enENC(): Fórmula incorrecta!')
    B = B.split('Y')
    B = [c.split('O') for c in B]
    return B

def tseitin(A): # Algoritmo de transformación de Tseitin, que toma una fórmula A en notación inorder y devuelve su equivalente en FNC utilizando letras proposicionales nuevas.
    '''
    Algoritmo de transformacion de Tseitin
    Input: A (cadena) en notacion inorder
    Output: B (cadena), Tseitin
    '''
    # Creamos letras proposicionales nuevas
    f = inorder_to_tree(A)
    letrasp = f.letras()
    cods_letras = [ord(x) for x in letrasp]
    m = max(cods_letras) + 256
    letrasp_tseitin = [chr(x) for x in range(m, m + f.num_conec())]
    letrasp = list(letrasp) + letrasp_tseitin
    L = [] # Inicializamos lista de conjunciones
    Pila = [] # Inicializamos pila
    i = -1 # Inicializamos contador de variables nuevas
    s = A[0] # Inicializamos símbolo de trabajo
    while len(A) > 0: # Recorremos la cadena
        # print("Pila:", Pila, " L:", L, " s:", s)
        if (s in letrasp) and (len(Pila) > 0) and (Pila[-1]=='-'):
            i += 1
            atomo = letrasp_tseitin[i]
            Pila = Pila[:-1]
            Pila.append(atomo)
            L.append(atomo + "=-" + s)
            A = A[1:]
            if len(A) > 0:
                s = A[0]
        elif s == ')':
            w = Pila[-1]
            O = Pila[-2]
            v = Pila[-3]
            Pila = Pila[:len(Pila)-4]
            i += 1
            atomo = letrasp_tseitin[i]
            L.append(atomo + "=(" + v + O + w + ")")
            s = atomo
        else:
            Pila.append(s)
            A = A[1:]
            if len(A) > 0:
                s = A[0]
    if i < 0:
        atomo = Pila[-1]
    else:
        atomo = letrasp_tseitin[i]
    B = [[[atomo]]] + [a_clausal(x) for x in L]
    B = [val for sublist in B for val in sublist]
    return B

def complemento(l): # Toma un literal l y devuelve su complemento.
    if '-' in l:
        return l[1:]
    else:
        return '-' + l
    
def eliminar_literal(S, l): # Elimina todas las cláusulas que contienen el literal l en el conjunto de cláusulas S.
    S1 = [c for c in S if l not in c]
    lc = complemento(l)
    return [[p for p in c if p != lc] for c in S1]

def extender_I(I, l): # Extiende una interpretación I con el valor del literal l según su complemento.
    I1 = {k:I[k] for k in I if k != l}
    if '-' in l:
        I1[l[1:]] = False
    else:
        I1[l] = True
    return I1

def unit_propagate(S, I): # Elimina las cláusulas unitarias de un conjunto de cláusulas S y ajusta la interpretación I en consecuencia.
    '''
    Algoritmo para eliminar clausulas unitarias de un conjunto de clausulas, manteniendo su satisfacibilidad
    Input: 
        - S, conjunto de clausulas
        - I, interpretacion (diccionario {literal: True/False})
    Output: 
        - S, conjunto de clausulas
        - I, interpretacion (diccionario {literal: True/False})
    '''
    while [] not in S:
        l = ''
        for x in S:
            if len(x) == 1:
                l = x[0]
                S = eliminar_literal(S, l)
                I = extender_I(I, l)
                break
        if l == '': # Se recorrió todo S y no se encontró unidad
            break
    return S, I

def dpll(S, I): # Algoritmo DPLL para verificar la satisfacibilidad de un conjunto de cláusulas S y encontrar un modelo de la misma. Utiliza recursión
                # y búsqueda aleatoria si es necesario. Devuelve el resultado de satisfacibilidad y una interpretación válida.
    '''
    Algoritmo para verificar la satisfacibilidad de una formula, y encontrar un modelo de la misma
    Input: 
        - S, conjunto de clausulas
        - I, interpretacion (diccionario literal->True/False)
    Output: 
        - String, Satisfacible/Insatisfacible
        - I ,interpretacion (diccionario literal->True/False)
    '''
    S, I = unit_propagate(S, I)
    if [] in S: return "Insatisfacible", {}
    if len(S) == 0: return "Satisfacible", I
    lit_en_S = list(set([p if len(p) == 1 else p[1] for c in S for p in c]))
    lit_en_S_not_in_I = [p for p in lit_en_S if p not in I.keys()]
    l = choice(lit_en_S_not_in_I)
    S_ = eliminar_literal(S,l)
    I_ = extender_I(I,l)
    result, I__ = dpll(S_,I_)
    if result == "Satisfacible":
        return "Satisfacible", I__
    else:
        l = complemento(l)
        S_ = eliminar_literal(S, l)
        I_ = extender_I(I, l)
        return dpll(S_,I_)