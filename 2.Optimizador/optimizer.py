"""


>>> obj = Optimizer()
>>> obj.set_working_dir(working_dir="Tests/Test1/")
>>> obj.load_data()

### >>> obj.distancias
>>> obj.pepito()

"""

import configparser
import pandas



import glob

class Optimizer():
    """Optimizador

    """
    def __init__(self):
        """Esta función crea la clase y lee la informacion relevante del
        directorio de trabajo. """
        self.working_dir = None
        self.selfano_analisis = None
        self.uso_max_transformador = None
        self.costo_hora_desmontaje = None
        self.costo_hora_montaje = None
        self.costo_hora_transporte = None
        self.tiempo_de_recuperacion = None
        self.velocidad = None


    def set_working_dir(self, working_dir):
        """Establece el directorio de trabajo por defecto"""
        self.working_dir = working_dir

    def pepito(self):
        print ("hola Juan David")


    def load_data(self):
        """Lee los datos del directorio de trabajo.

        Estructura de los archivos:
        ---------------------------------------------------------------------

        * carac_tecn_transf.csv
             fases
             capacidad_kVA
             costo_a_nuevo
             tiempo_montaje_h
             tiempo_desmontaje_h


        * costos.csv
             fabricante
             fases
             capacidad_kVA
             uso_transf
             perdidas_tecnicas
             perdida_vida_util
             fila

        * distancias.csv
             Nodo1
             Nodo2
             km

        * inventario_transformadores.csv
             id_transformador
             fabricante
             fases
             capacidad_kVA
             anos_de_uso
             id_nodo
             vida_util_teorica_anos

        * nodos.csv
             id_nodo
             latitud
             longitud
             tension_nodo
             carga_equiv_promedio_kVA
             carga_maxima_kVA
             carga_reconocida_CRE

        * red.csv
             Nodo1
             Nodo2

        * tarifa_distribuidor.csv
             tension_nodo
             tarifa_kWh

        * tarifas_creg.csv
             fases
             capacidad_kVA
             costos_reconocidos_CREG

        """

        ## parametros globales
        parser = configparser.ConfigParser()
        parser.read(self.working_dir + 'input/params.txt')

        ## asigna los parametros globales
        self.ano_analisis = parser['DEFAULT']['ano_analisis']
        self.uso_max_transformador = parser['DEFAULT']['uso_max_transformador']
        self.costo_hora_desmontaje = parser['DEFAULT']['costo_hora_desmontaje']
        self.costo_hora_montaje = parser['DEFAULT']['costo_hora_montaje']
        self.costo_hora_transporte = parser['DEFAULT']['costo_hora_transporte']
        self.tiempo_de_recuperacion = parser['DEFAULT']['tiempo_de_recuperacion']
        self.velocidad = parser['DEFAULT']['velocidad']

        ## tablas de datos
        self.nodos = pandas.read_csv(self.working_dir + "input/nodos.csv", sep=';', decimal=',')
        self.inventario_transf = pandas.read_csv(self.working_dir + "input/inventario_transformadores.csv", sep=';', decimal=',')
        self.caractecntransf = pandas.read_csv(self.working_dir + "input/carac_tecn_transf.csv", sep=';', decimal=',')
        self.costos = pandas.read_csv(self.working_dir + "input/costos.csv", sep=';', decimal=',')
        self.tarifadistribuidor = pandas.read_csv(self.working_dir + "input/tarifa_distribuidor.csv", sep=';', decimal=',')
        self.tarifascreg = pandas.read_csv(self.working_dir + "input/tarifas_creg.csv", sep=';', decimal=',')
        self.distancias = pandas.read_csv(self.working_dir + "input/distancias.csv", sep=';', decimal=',')

        ## claves de tablas
        self.inventario_transf['id_caract'] = self.inventario_transf['fases'].map(str) + "-" + self.inventario_transf['capacidad_kVA'].map(str)
        self.caractecntransf['id_caract'] =  self.caractecntransf['fases'].map(str) + "-" + self.caractecntransf['capacidad_kVA'].map(str)
        self.costos['id_costos'] =  self.costos['fabricante'].map(str) + "-" +  self.costos['fases'].map(str) + "-" +                                     self.costos['capacidad_kVA'].map(str) + "-" +   self.costos['uso_transf'].map(str)

        self.inventario_transf['id_costos'] =  self.inventario_transf['fabricante'].map(str) + "-" + self.inventario_transf['fases'].map(str) + "-" +  self.inventario_transf['capacidad_kVA'].map(str) + "-" + self.inventario_transf['anos_de_uso'].map(str)


    def __repr__(self):
        txt = []
        txt.append("Parametros generales:")
        txt.append("  Working dir: " + self.working_dir)
        txt.append("  ano_analisis: " + self.ano_analisis)
        txt.append("  uso_max_transformador: " + self.uso_max_transformador)
        txt.append("  costo_hora_montaje:" + self.costo_hora_montaje)
        txt.append("  costo_hora_desmontaje: " + self.costo_hora_desmontaje)
        txt.append("  costo_hora_transporte: " + self.costo_hora_transporte)
        txt.append("  costo_hora_transporte: " + self.costo_hora_transporte)
        txt.append("  tiempo_de_recuperacion: " + self.tiempo_de_recuperacion)
        txt.append("  velocidad: " + self.velocidad)
        return '\n'.join(txt)


    def calcular_costos_config(self):
        sol_actual = pandas.merge(self.inventario_transf, self.nodos, on='id_nodo', how='outer')
        sol_actual = pandas.merge(sol_actual, self.caractecntransf, on='id_caract', how='outer')
        sol_actual = pandas.merge(sol_actual, self.tarifadistribuidor, on='tension_nodo', how='outer')
        sol_actual = pandas.merge(sol_actual, self.costos, on='id_costos', how='outer')

        ## sol_actual['']


    def run(self):
        """Ejecuta la rutina de optimizacion.
        """

        pass
