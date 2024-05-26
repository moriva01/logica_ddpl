from paquete_logico import *
import matplotlib as mplt 
import matplotlib.pyplot as plt 
from matplotlib import patches
from types import MethodType
from itertools import combinations, product

def escribirBombillas(self, Lit):
    """
    Función que sobreescribe el método `escribir` del descriptor para el problema de las bombillas.

    Args:
      Lit: Literal que representa una proposición en el problema de las bombillas.

    Returns:
      Cadena que describe la proposición de manera más clara para el usuario.
    """
    # Obteniendo literal dependiendo de si es negación o no
    if Lit[0] == '-':
        neg = 'no'
        b,e = self.unravel(Lit[1:])
    else: 
        neg = ''
        b,e = self.unravel(Lit)
    # Definiendo j dependiendo del jugador
    estados = ["Encendido", "Apagado", "Caliente"]
        
    # Retornando formated string 
    return f"El bomillo {b + 1} está {estados[e]}"

def escribirInterruptor(self, Lit):
    """
    Función que sobreescribe el método `escribir` del descriptor para el problema de las bombillas.

    Args:
      Lit: Literal que representa una proposición en el problema de las bombillas.

    Returns:
      Cadena que describe la proposición de manera más clara para el usuario.
    """
    # Obteniendo literal dependiendo de si es negación o no
    if Lit[0] == '-':
        neg = 'no'
        b,e = self.unravel(Lit[1:])
    else: 
        neg = ''
        i,e = self.unravel(Lit)
    # Definiendo j dependiendo del jugador
    estados = ["Encendido", "Apagado", "Encendido y luego apagado"]
        
    # Retornando formated string 
    return f"El interruptor {i + 1} está {estados[e]}"
    
def escribirPertenencia(self, Lit):
    """
    Función que sobreescribe el método `escribir` del descriptor para el problema de las bombillas.

    Args:
      Lit: Literal que representa una proposición en el problema de las bombillas.

    Returns:
      Cadena que describe la proposición de manera más clara para el usuario.
    """
    # Obteniendo literal dependiendo de si es negación o no
    if Lit[0] == '-':
        neg = 'no'
        b,e = self.unravel(Lit[1:])
    else: 
        neg = ''
        b,i = self.unravel(Lit)
        
    # Retornando formated string 
    return f"El Interruptor {i + 1} pertenece a bombillo {b + 1}"



class Bombillas:
    #Constructor 
    def __init__(self):
        # Instanciando descriptor para clase
        self.Bombillos = Descriptor([3,3])
        self.Pertenece = Descriptor([3,3], chrInit = 256 + 9)
        self.Interruptor = Descriptor([3,3], chrInit = 256 + 18)
        # Modificando método describir para instancia especifica del descriptor
        self.Bombillos.escribir = MethodType(escribirBombillas,self.Bombillos)
        self.Pertenece.escribir = MethodType(escribirPertenencia,self.Pertenece)
        self.Interruptor.escribir = MethodType(escribirInterruptor,self.Interruptor)
        # Lista de reglas
        self.regla = [
            self.regla1(),
            self.regla2(),
            self.regla3(),
            self.regla4(),
            self.regla5(),
            self.regla6()
        ]
        
    # Regla 1: Si una bombilla está encendida, su interruptor también debe estar encendido.
    def regla1(self):
        regla1 = []
        for b in range(3):
            for i in range(3):
                estados = [ f"({self.Bombillos.ravel([b,e])}Y{self.Interruptor.ravel([i, e])})" for e in range(3)]
                regla1.append(f"({self.Pertenece.ravel([b,i])}={Otoria(estados)})")
        return Ytoria(regla1)

    # Regla2: A todo bombillo le pertenece algún interruptor
    def regla2(self):
        regla2 = []
        for b in range(3):
            regla2.append(Otoria([self.Pertenece.ravel([b,i]) for i in range(3)]))
        return Ytoria(regla2)

    # Regla3: Todo interruptor pertenece a algún bombillo
    def regla3(self):
        regla3 = []
        for i in range(3):
            regla3.append(Otoria([self.Pertenece.ravel([b,i]) for b in range(3)]))
        return Ytoria(regla3)

    # Regla3: Un bombillo no puede tener más de un interruptor
    def regla4(self):
        regla5 = []
        for b in range(3):
            for i in range(3):
                otrosInterruptores = [self.Pertenece.ravel([b,i_]) for i_ in range(3) if i != i_]
                regla5.append(f"({self.Pertenece.ravel([b,i])}>-{Otoria(otrosInterruptores)})")
        return Ytoria(regla5)

    # Regla3: Un interruptor no pertenece a más de un bombillo
    def regla5(self):
        regla5 = []
        for i in range(3):
            for b in range(3):
                otrasBombillas = [self.Pertenece.ravel([b_,i]) for b_ in range(3) if b != b_]
                regla5.append(f"({self.Pertenece.ravel([b,i])}>-{Otoria(otrasBombillas)})")
        return Ytoria(regla5)

    def regla6(self):
        return self.Bombillos.ravel([1,0])

    def escribirFormula(self, A):
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
                try:
                    valNum = ord(c)
                    if valNum < 256 + 9:
                        vis.append(self.Bombillos.escribir(c))
                    elif valNum < 256 + 18:
                        vis.append(self.Pertenece.escribir(c))
                    else:
                        vis.append(self.Interruptor.escribir(c))
                        
                except:
                    raise("¡Caracter inválido!")
        return ''.join(vis)

    # Método para presentar una interpretación de manera visual 
    def visualizar(self, I):         
        # Creando figura 
        fig, ax = plt.subplots(figsize = (6, 6))
        
        # Escondiendo etiquetas de ejes
        plt.xticks([])
        plt.yticks([])
        coloresCon = ['black', 'blue', 'green']
        i = 0
        for c in I:
            if not (ord(c) < 256 + 27 and I[c]):
                continue
            valNum = ord(c)
            if valNum < 256 + 9:
                b, e = self.Bombillos.unravel(c)
                colors = [ "yellow", "gray", "orange"]
                ax.add_patch(patches.Circle((1/3 * b + 1/6, 3/4), radius=1/9, color=colors[e]))
            elif valNum < 256 + 18:
                b, i = self.Pertenece.unravel(c)
                ax.add_line(mplt.lines.Line2D([1/3 * i + 1/6, 1/3 * b + 1/6], [1/8 + 2/9, 3/4 - 1/9], linewidth = 1, color = coloresCon[i]))
                i+=1
            else:
                i, e = self.Interruptor.unravel(c)
                colors = ["green", "black", "red"]
                ax.add_patch(patches.Rectangle((1/3 * i + 1/6 - 1 /9, 1/8), height=2/9, width = 2/9, color=colors[e]))

        plt.show()

