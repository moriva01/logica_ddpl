from paquete_logico import *
import matplotlib as mplt # Es una biblioteca para crear visualizaciones estáticas, animadas e interactivas en Python.
import matplotlib.pyplot as plt # Es un módulo de alto nivel que proporciona una interfaz orientada a objetos para crear visualizaciones.
from matplotlib import patches # Contiene clases que representan formas geométricas como rectángulos, círculos y polígonos.
from types import MethodType # Esta función permite crear un objeto de método utilizando una función.
from itertools import combinations, product # Proporciona una función que genera todas las combinaciones posibles de un iterable.
                                            # Proporciona una función que calcula el producto cartesiano de varios iterables.

def escribirBombillas(self, Lit): # ----------------------------------------------- escritor bombillas
    # Obteniendo literal dependiendo de si es negación o no
    if Lit[0] == '-':
        neg = 'no'
        b,e = self.unravel(Lit[1:])
    else: 
        neg = ''
        b,e = self.unravel(Lit)
    # Definiendo estados de las bombillas
    estados = ["Encendido", "Apagado", "Caliente"]
        
    # Retornando como string 
    return f"El bomillo {b + 1} está {estados[e]}"

def escribirInterruptor(self, Lit): # ----------------------------------------------- escritor interruptor
    # Obteniendo literal dependiendo de si es negación o no
    if Lit[0] == '-':
        neg = 'no'
        b,e = self.unravel(Lit[1:])
    else: 
        neg = ''
        i,e = self.unravel(Lit)
    # Definiendo estados de interruptor
    estados = ["Encendido", "Apagado", "Encendido y luego apagado"]
        
    # Retornando como string  
    return f"El interruptor {i + 1} está {estados[e]}"
    
def escribirPertenencia(self, Lit): # ----------------------------------------------- escritor pertenencia
    # Obteniendo literal dependiendo de si es negación o no
    if Lit[0] == '-':
        neg = 'no'
        b,e = self.unravel(Lit[1:])
    else: 
        neg = ''
        b,i = self.unravel(Lit)
        
    # Retornando como string
    return f"El Interruptor {i + 1} pertenece a bombillo {b + 1}"



class Bombillas:
    #Constructor 
    def __init__(self):
        # Instanciando descriptores para clase
        self.Bombillos = Descriptor([3,3])
        self.Pertenece = Descriptor([3,3], chrInit = 256 + 9)
        self.Interruptor = Descriptor([3,3], chrInit = 256 + 18)
        # Modificando método describir para que escriba cada descriptor
        self.Bombillos.escribir = MethodType(escribirBombillas,self.Bombillos)
        self.Pertenece.escribir = MethodType(escribirPertenencia,self.Pertenece)
        self.Interruptor.escribir = MethodType(escribirInterruptor,self.Interruptor)
        # Lista de reglas
        self.regla = [
            self.regla1(),
            self.regla2(),
            self.regla3(),
            self.regla4(),
            self.regla5()
            #,self.regla6()# esta regla es para poner casos de inicio
        ]
        
    
    def regla1(self):# Regla 1: Si una bombilla está encendida, su interruptor también debe estar encendido.
        regla1 = []
        for b in range(3):
            for i in range(3):
                estados = [ f"({self.Bombillos.ravel([b,e])}Y{self.Interruptor.ravel([i, e])})" for e in range(3)]
                regla1.append(f"({self.Pertenece.ravel([b,i])}={Otoria(estados)})")
        return Ytoria(regla1)

   
    def regla2(self):  # Regla2: todo bombillo le pertenece algún interruptor
        regla2 = []
        for b in range(3):
            regla2.append(Otoria([self.Pertenece.ravel([b,i]) for i in range(3)]))
        return Ytoria(regla2)

    
    def regla3(self): # Regla3: Todo interruptor pertenece a algún bombillo
        regla3 = []
        for i in range(3):
            regla3.append(Otoria([self.Pertenece.ravel([b,i]) for b in range(3)]))
        return Ytoria(regla3)

   
    def regla4(self):  # Regla4: Un bombillo no puede tener más de un interruptor
        regla4 = []
        for b in range(3):
            for i in range(3):
                otrosInterruptores = [self.Pertenece.ravel([b,i_]) for i_ in range(3) if i != i_]
                regla4.append(f"({self.Pertenece.ravel([b,i])}>-{Otoria(otrosInterruptores)})")
        return Ytoria(regla4)

    
    def regla5(self): # Regla5: Un interruptor no pertenece a más de un bombillo
        regla5 = []
        for i in range(3):
            for b in range(3):
                otrasBombillas = [self.Pertenece.ravel([b_,i]) for b_ in range(3) if b != b_]
                regla5.append(f"({self.Pertenece.ravel([b,i])}>-{Otoria(otrasBombillas)})")
        return Ytoria(regla5)

    def regla6(self): # casos de problemas de inicio
        return self.Bombillos.ravel([1,0]) and self.Interruptor.ravel([0,2])# bombilla 2 encendida (caso simulado ejemplo)

    def escribirFormula(self, A): # interpretar todo como una formula in order
        vis = []
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
                try:# filtro de las letras propocisionales
                    valNum = ord(c)# toma la letra en su forma de numeros
                    if valNum < 256 + 9:
                        vis.append(self.Bombillos.escribir(c))# bombillos (9 estados)
                    elif valNum < 256 + 18:
                        vis.append(self.Pertenece.escribir(c))# pertenece (los otros 9 estados)
                    else:
                        vis.append(self.Interruptor.escribir(c)) # interruptor (los otros estados)
                        
                except:
                    raise("¡Caracter inválido!")
        return ''.join(vis)

    def visualizar(self, I): # Método para presentar una interpretación de manera visual         
         
        fig, ax = plt.subplots(figsize = (6, 6)) # Creando figura
        
        # Escondiendo etiquetas de ejes
        plt.xticks([])
        plt.yticks([])
        
        
        coloresCon = ["black", "black", "black"]# colores de la relacion
        i = 0
        for c in I:
            if not (ord(c) < 256 + 27 and I[c]):
                continue
            valNum = ord(c)
            if valNum < 256 + 9:
                b, e = self.Bombillos.unravel(c)
                colors = [ "yellow", "gray", "orange"] # colores bombillos (depende del estado)
                ax.add_patch(patches.Circle((1/3 * b + 1/6, 3/4), radius=1/9, color=colors[e]))# dibuja circulos como bombillos
            elif valNum < 256 + 18:
                b, i = self.Pertenece.unravel(c)
                ax.add_line(mplt.lines.Line2D([1/3 * i + 1/6, 1/3 * b + 1/6], [1/8 + 2/9, 3/4 - 1/9], linewidth = 1, color = coloresCon[i]))# dibuja lineas como relacion interruptor - bombilla
                i+=1
            else:
                i, e = self.Interruptor.unravel(c)
                colors = ["green", "blue", "purple"] # colores interruptor (depende del estado)
                ax.add_patch(patches.Rectangle((1/3 * i + 1/6 - 1 /9, 1/8), height=2/9, width = 2/9, color=colors[e]))# dibuja rectangulos como interruptores

        plt.show()# mostrar el grafico de esa relacion y sus estados

