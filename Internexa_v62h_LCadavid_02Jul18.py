
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('reset', '-f')

import os
import numpy as np
import pandas as pd
import math
from math import e

import configparser


# In[23]:


get_ipython().run_line_magic('clear', '')
"""
Comentarios sobre el tutorial

Aca se crea la clase
>>> m = Optimizer()

La funcion `set_working_dir` permite cambiar el directorio de trabajo.
>>> m.set_working_dir(working_dir="../Tests/Test1/")

>>> m.run()
>>> m.ctsolini # doctest: +ELLIPSIS
608270716.35...

>>> m.ctsolfin # doctest: +ELLIPSIS
581168132.54...

>>> x = pd.read_csv(m.working_dir + "output/solucion_final.csv", sep=',', decimal='.')
>>> x.head() # doctest: +NORMALIZE_WHITESPACE
   Unnamed: 0  id_n  id_t           cpt           cvu         coper     cperm  \\
0           0   1.0   9.0  2.358724e+07  3.316718e+06  2.690396e+07  381000.0   
1           1   2.0   2.0  1.053354e+05  2.397708e+04  1.293125e+05       0.0   
2           2   3.0   3.0  1.369407e+05  2.877250e+04  1.657131e+05       0.0   
3           3   4.0  30.0  1.531476e+07  1.750192e+06  1.706495e+07  381000.0   
4           4   5.0  13.0  2.655321e+07  3.740291e+06  3.029350e+07  381000.0   
<BLANKLINE>
      cdete  eval  perm  bloq  capa_t     cmax_n  
0  238464.0   1.0   1.0   0.0    45.0  19.380000  
1       0.0   1.0   0.0   0.0    75.0   8.058000  
2       0.0   1.0   0.0   0.0   112.5   3.876000  
3  101400.0   1.0   1.0   0.0    10.0   8.926133  
4  286156.8   1.0   1.0   0.0    50.0  24.022133  
"""
class Optimizer():
    """Optimizador
    """
    def __init__(self):
        """Esta función crea la clase y lee la informacion relevante del directorio de trabajo.
        """
        pass
        
    def set_working_dir(self, working_dir):
        """Establece el directorio de trabajo por defecto.
        
        Args:
            working_dir (str): directorio de trabajo.
            
        """
        self.working_dir = working_dir
        self.pathoutput = working_dir + 'output/'

        
    def load_data(self):
        """Lee los datos del directorio de trabajo.
        """
        
        ## definicion del archivo txt donde estan los parametros
        parser = configparser.ConfigParser()
        parser.read(self.working_dir + 'input/params.txt')

        ## parametros globales
        self.HSCD = float(parser['CALCULOS']['horas_sobrecarga_dia'])
        self.PVDT = float(parser['CALCULOS']['perdida_vida_diaria_teorica'])
        self.TNTR = float(parser['CALCULOS']['temperatura_normal_trafo'])
        self.TAMB = float(parser['CALCULOS']['temperatura_ambiente'])
        self.PDRE = float(parser['CALCULOS']['probabilidad_deterioro_reubicacion'])
        self.FCMX = float(parser['CALCULOS']['factor_carga_maxima'])
        self.FCPR = float(parser['CALCULOS']['factor_carga_promedio'])

        ## calculos con parametros globales
        self.HVUT = 24 / self.PVDT
        self.AVUT = self.HVUT / (24*365) 

        ##
        ## Resoluciones 818 y 819
        ##
        
        ##    Transformadores monofasicos - Perdidas en vacio
        ##
        self.P1FVAC1 = float(parser['RES818819']['Par_1f_vac_1'])
        self.P1FVAC2 = float(parser['RES818819']['Par_1f_vac_2'])

        ##
        ##    Transformadores monofasicos - Perdidas con carga
        ##        
        self.P1FCAR1 = float(parser['RES818819']['Par_1f_car_1'])
        self.P1FCAR2 = float(parser['RES818819']['Par_1f_car_2'])
        self.P1FCAR3 = float(parser['RES818819']['Par_1f_car_3'])
        self.P1FCAR4 = float(parser['RES818819']['Par_1f_car_4'])

        ##
        ##    Transformadores trifasicos -- Perdidas en vacio
        ##
        self.P3FVAC11 = float(parser['RES818819']['Par_3f_vac_11'])
        self.P3FVAC12 = float(parser['RES818819']['Par_3f_vac_12'])
        self.P3FVAC21 = float(parser['RES818819']['Par_3f_vac_21'])
        self.P3FVAC22 = float(parser['RES818819']['Par_3f_vac_22'])
        self.P3FVAC31 = float(parser['RES818819']['Par_3f_vac_31'])
        self.P3FVAC32 = float(parser['RES818819']['Par_3f_vac_32'])

        ##
        ##    Transformadores trifasicos - Perdidas con carga
        ##        
        self.P3FCAR11 = float(parser['RES818819']['Par_3f_car_11'])
        self.P3FCAR12 = float(parser['RES818819']['Par_3f_car_12'])
        self.P3FCAR13 = float(parser['RES818819']['Par_3f_car_13'])
        self.P3FCAR21 = float(parser['RES818819']['Par_3f_car_21'])
        self.P3FCAR22 = float(parser['RES818819']['Par_3f_car_22'])
        self.P3FCAR31 = float(parser['RES818819']['Par_3f_car_31'])
        self.P3FCAR32 = float(parser['RES818819']['Par_3f_car_32'])

        ##
        ## tablas de datos
        ##
        self.nodos = pd.read_csv(self.working_dir + "input/nodos.csv", sep=',', decimal='.')
        self.inv = pd.read_csv(self.working_dir + "input/inventario_transformadores.csv", sep=',', decimal='.')
        self.cartectraf = pd.read_csv(self.working_dir + "input/carac_tecn_transf.csv", sep=',', decimal='.')
        self.vu = pd.read_csv(self.working_dir + "input/vida_util.csv", sep=',', decimal='.')

        ##
        ## nombres de las columnas de las tablas de datos
        ##
        self.nodos.columns = ['id_n', 'id_n_Internexa','lat','lon','tension','cpro_n','cmax_n','cremcreg','dmda_n','cens','cred','tusu','pkwh_n']
        self.inv.columns = ['id_t', 'id_t_Internexa','fab','fase_t','tais','capa_t','vprim','vsecu','ffab','anus','viut_t','id_n_Internexa','tacr_t','creu_t','finst']
        self.vu.columns = ['tgrc', 'fase_t','lipo','lspo','cpre','dura','cpor','tmpc','tmac']
        self.cartectraf.columns = ['fase_t', 'capa_t','cnue_t']

        ## 
        ## adecuacion de las tablas para facilidad en calculos
        ##
        self.inv = self.inv.merge(self.nodos[['id_n','id_n_Internexa']], on = 'id_n_Internexa',how = 'left')

        ## calcular carga maxima y carga promedio de los nodos
        self.nodos['cpro_n'] = self.nodos['dmda_n'] / 30 * self.FCPR
        self.nodos['cmax_n'] = self.nodos['dmda_n'] / 30 * self.FCMX
        
        ## indicar grupo del trafo para calculo de las perdidas de transformacion
        self.inv['grpt_t'] = 1
        self.inv.loc[(self.inv.fase_t == 3) & (self.inv.capa_t >= 150), 'grpt_t'] = 2
        self.inv.loc[(self.inv.fase_t == 3) & (self.inv.capa_t >= 800), 'grpt_t'] = 3

        ## indicar grupo del trafo para calculo de las perdidas de vida util
        self.inv['grpv_t'] = 1
        self.inv.loc[(self.inv.fase_t == 1) & (self.inv.capa_t > 50), 'grpv_t'] = 2
        self.inv.loc[(self.inv.fase_t == 3) & (self.inv.capa_t >= 150), 'grpv_t'] = 2
        self.inv.loc[(self.inv.fase_t == 3) & (self.inv.capa_t >= 500), 'grpv_t'] = 3
                
        ## calcular vida util restante del trafo en meses
        self.inv['viut_t'] = self.AVUT
        self.inv['viur_t'] = (self.inv.viut_t - self.inv.anus) * 12
        self.inv.loc[self.inv.viur_t < 0, 'viur_t'] = 1

        ## indicar grupo de vida util
        self.vu['grpv_t'] = 1
        self.vu.loc[(self.vu.fase_t == 1) & (self.vu.lipo >= 50), 'grpv_t'] = 2
        self.vu.loc[(self.vu.fase_t == 3) & (self.vu.lipo >= 150),'grpv_t'] = 2
        self.vu.loc[(self.vu.fase_t == 3) & (self.vu.lipo >= 500), 'grpv_t'] = 3

        ## armar keys para busquedas
        self.cartectraf['faca'] = self.cartectraf.fase_t.map(str) + "-" + self.cartectraf.capa_t.map(str)
        self.vu['tfcg'] = self.vu.tgrc.map(str) + "-" + self.vu.fase_t.map(str) + "-" + self.vu.cpre.map(str) + "-" + self.vu['grpv_t'].map(str)
   
    
    def parnd(self, id_n):
        """Obtiene los parametros de un nodo.
        
        Args:
            id_n (int): id del nodo.

        Returns:
            cmax_n (float): carga maxima que soporta el nodo.
            cpro_n (float): carga promedio que soporta el nodo.
            pkwh_n (float): precio por kWh de la electricidad que sirve el nodo.
        
        """
        cmax_n = float(self.nodos[self.nodos.id_n == id_n]['cmax_n'])
        cpro_n = float(self.nodos[self.nodos.id_n == id_n]['cpro_n'])    
        pkwh_n = float(self.nodos[self.nodos.id_n == id_n]['pkwh_n']) 
        return (cmax_n,cpro_n,pkwh_n)

    
    def partf(self, id_t):
        """Obtiene los parametros de un trafo.

        Args:
            id_t (int): id del trafo.

        Returns:
            capa_t (float): capacidad del trafo.
            fase_t (int): numero de fases del trafo.
            viut_t (int): vida utuil teorica del trafo.
            nodo_t (int): nodo al que se encuentra asociado el trafo.
            creu_t (float): costo de la actividad de reubicacion del trafo.
            viur_t (float): vida util restante del trafo.
            grpt_t (int): grupo al que pertenece el trafo para el calculo de las perdidas de transformacion.
            grpv_t (int): grupo al que pertenece el trafo para el calculo de las perdidas de vida util.
            faca_t (str): key fase-capacidad.
            cnue_t (int): precio por kWh de la electricidad que sirve el nodo.
        
        """
        capa_t = float(self.inv[self.inv.id_t == id_t]['capa_t'])
        fase_t = int(self.inv[self.inv.id_t == id_t]['fase_t'])
        viut_t = int(self.inv[self.inv.id_t == id_t]['viut_t'])
        nodo_t = int(self.inv[self.inv.id_t == id_t]['id_n'])
        creu_t = float(self.inv[self.inv.id_t == id_t]['creu_t'])
        viur_t = float(self.inv[self.inv.id_t == id_t]['viur_t'])
        grpt_t = int(self.inv[self.inv.id_t == id_t]['grpt_t'])
        grpv_t = int(self.inv[self.inv.id_t == id_t]['grpv_t'])
        faca_t = str(fase_t) + '-' + str(capa_t)
        cnue_t = int(self.cartectraf[self.cartectraf.faca == faca_t]['cnue_t'])
        return (capa_t, fase_t, viut_t, nodo_t, creu_t, viur_t, grpt_t, grpv_t, faca_t, cnue_t)

    
    def cospt(self, id_n, id_t):
        """Calcula los costos de las perdidas de transformacion de un par nodo*trafo.

        Args:
            id_n (int): id del nodo.
            id_t (int): id del trafo.

        Returns:
            cpt_nt (float): costos de perdidas de transformacion en pesos.
        
        """
        if id_n == 999999:
            cpt_nt = 0
        else:
            # hallar parametros del nodo y del trafo
            cmax_n,cpro_n,pkwh_n = self.parnd(id_n)
            capa_t,fase_t,viut_t,nodo_t,creu_t,viur_t,grpt_t,grpv_t,faca_t,cnue_t = self.partf(id_t)
            futi_nt = cmax_n / capa_t

            # calcular perdidas nominales en vacio y perdidas nominales con carga en funcion de las fases y el grupo en la fase
            if fase_t == 1:
                pnvac = self.P1FVAC1 * capa_t ** self.P1FVAC2
                pncar = self.P1FCAR1 * capa_t ** 3 + self.P1FCAR2 * capa_t ** 2 + self.P1FCAR3 * capa_t + self.P1FCAR4
            else:
                if grpt_t == 1:
                    pnvac = self.P3FVAC11 * capa_t ** self.P3FVAC12
                    pncar = self.P3FCAR11 * capa_t ** 2 + self.P3FCAR12 * capa_t + self.P3FCAR13
                if grpt_t == 2:
                    pnvac = self.P3FVAC21 * capa_t ** self.P3FVAC22
                    pncar = self.P3FCAR21 * capa_t + self.P3FCAR22
                if grpt_t == 3:
                    pnvac = self.P3FVAC31 * capa_t ** self.P3FVAC32
                    pncar = self.P3FCAR31 * capa_t + self.P3FCAR32

            # calcular las perdidas en hierro y cobre en unidades W 
            pfeW = pnvac
            pcuW = pncar * futi_nt ** 2
            ptrW = pfeW + pcuW

            # monetizacion de las perdidas
            cpt_nt = ptrW / 1000 * pkwh_n * 24 * 30 * viur_t
        return cpt_nt
    
    
    def cospv(self, id_n, id_t):
        """Calcula los costos de las perdidas de vida util de un par nodo*trafo

        Args:
            id_n (int): id del nodo.
            id_t (int): id del trafo.

        Returns:
            cpt_vu (float): costos de perdidas de vida util en pesos.
        
        """
        if id_n == 999999:
            cvu_nt = 0
        else:
            # hallar parametros del nodo y del trafo
            cmax_n,cpro_n,pkwh_n = self.parnd(id_n)
            capa_t,fase_t,viut_t,nodo_t,creu_t,viur_t,grpt_t,grpv_t,faca_t,cnue_t = self.partf(id_t)

            # calcular la carga precedente y el factor de utilizacion
            cpre_nt = cpro_n / capa_t
            futi_nt = cmax_n / capa_t

            # aproximar la carga precedente a los valores de la norma GTC50
            if cpre_nt < ((0.5 + 0.75) / 2):
                cpre_nt = 0.5
            else:
                if cpre_nt < ((0.75 + 0.9) / 2):
                    cpre_nt = 0.75
                else:
                    cpre_nt = 0.9

            # calcular el porcentaje diario de perdida de vida util real en porcentaje
            key = str(self.TAMB) + '-' + str(fase_t) + '-' + str(cpre_nt) + '-' + str(grpv_t)
            theta = self.temperPC(futi_nt,key)
            fevej = (self.HSCD / 24) * (e**(15000/383 - 15000/(theta + 273))-1)
            pvdr = self.PVDT * (1 + fevej)

            # valorar perdida de vida util restante en pesos, durante lo que queda de vida util del trafo en el nodo 
            cvu_nt = viur_t * 30 * cnue_t * pvdr
        return cvu_nt
    
    
    def temperPC(self, futi_nt, key):
        """Calcula la temperatura del punto mas caliente dado un factor de utilizacion
        
        Args:
            futi_nt (float): factor de utilizacion.
            key (int): key TAMB - fase_t - cpre_nt - grpv_t.

        Returns:
            theta (int): temperatura del punto mas caliente.

        """
        tabvu = self.vu.loc[(self.vu.tfcg == str(key)) & (self.vu.dura <= self.HSCD)]
        ncargas = tabvu.shape[0]
        carga=futi_nt * 100
        theta=0
        if carga < tabvu['cpor'].min(): theta = self.TNTR
        if carga >= tabvu['cpor'].max(): theta = tabvu['tmpc'].max()
        if theta == 0:
            tabvu = tabvu.sort_values(['cpor'],ascending=[False])
            for index, row in tabvu.iterrows():
                if carga <= row['cpor']:
                    theta = row['tmpc']
                    break
        return theta 
    
    
    def costopermtf(self, id_t):
        """Calcula los costos de permutacion del trafo

        Args:
            id_t (int): id del trafo.

        Returns:
            cperm_t (float): costo de permutacion del trafo.
        
        """
        
        cperm_t = float(self.inv[self.inv.id_t == id_t]['creu_t'])
        return cperm_t


    def costodetetf(self, id_t):
        """Calcula los costos de deterioro de un trafo por reubicacion.

        Args:
            id_t (int): id del trafo.

        Returns:
            cdete_t (float): costo de deterioro del trafo.

        """
        cnue_t = self.partf(id_t)[9]
        cdete_t = cnue_t * self.PDRE
        return cdete_t


    def hallarparejasperm (self, sol):
        """ Encuentra dos parejas para hacer permutación. Una pareja es un par (nodo*trafo).

        Args:
            sol (tupla): solucion actual de la red.

        Returns:
            id_n1 (int): id del nodo de la pareja 1.
            id_t1 (int): id del trafo de la pareja 1.
            id_n2 (int): id del nodo de la pareja 2.
            id_t1 (int): id del trafo de la pareja 2.

        """
        id_t2 = 0
        while (id_t2 ==0):       
            # identificar el nodo mas costoso y su trafo para intercambio
            id_n1, id_t1 = self.ndmascostoso(sol)            
            id_n2, id_t2 = self.tfmascostoso(id_n1, sol)

            # si no encuentra un trafo adecuado para el cambio, se bloquea el nodo y repite con el siguiente mas costoso
            if id_t2 == 0:
                sol.at[sol.id_n == id_n1,'bloq']=1
        return (id_n1, id_t1, id_n2, id_t2)
    
    
    def ndmascostoso (self, sol):
        """Elige el nodo mas costoso aun no evaluado, junto con su trafo asociado.

        Args:
            sol (tupla): solucion actual de la red.

        Returns:
            id_n (int): id del nodo mas costoso.
            id_t (int): id del trafo asociado al nodo mas costoso.

        """
        # seleccionar los nodos potenciales
        solcopia = sol.copy()
        solcopia = solcopia[(solcopia['eval'] == 0)]
        solcopia = solcopia[(solcopia['bloq'] == 0)]
        solcopia = solcopia[(solcopia['coper'] > 0)]

        # seleccionar el mas costoso de los nodos
        id_n = 0
        id_t = 0
        if solcopia.shape[0] > 0:
            solcopia = solcopia.sort_values(['coper'],ascending=[False])
            id_n = int(solcopia.iloc[0,0])
            id_t = int(solcopia.iloc[0,1])
        return (id_n, id_t)


    def tfmascostoso (self, id_n, sol):
        """Elige el trafo mas costoso para hacer permutacion con un cierto nodo.

        Args:
            id_n (int): id del nodo.
            sol (tupla): solucion actual de la red.

        Returns:
            id_n2 (int): id del nodo asociado al trafo mas costoso.
            id_t2 (int): id del trafo mas costoso.
        
        """
        cmax_n = self.parnd(id_n)[0]
        id_t = int(sol[sol.id_n == id_n]['id_t'])
        capa_t = self.partf(id_t)[0]

        # seleccionar los transformadores potenciales
        solcopia = sol.copy()
        solcopia = solcopia[(solcopia.capa_t >= cmax_n)]
        solcopia = solcopia[(solcopia.cmax_n <= capa_t)]
        solcopia = solcopia[(solcopia.perm == 0)]
        solcopia = solcopia[(solcopia.bloq == 0)]
        solcopia = solcopia[(solcopia.id_n != id_n)]

        # restricción de cargabilidad minima de un trafo por auditoría de la CREG: 40%
        solcopia = solcopia[(solcopia.capa_t <= cmax_n / 0.4)]

        # seleccionar el mas costoso de los nodos de los trafos
        id_n2=0
        id_t2=0
        if solcopia.shape[0] > 0:
            solcopia = solcopia.sort_values(['coper'],ascending=[False])
            id_n2 = int(solcopia.iloc[0,0])
            id_t2 = int(solcopia.iloc[0,1])
        return (id_n2, id_t2)

    
    def cospermpar(self, id_t1, id_t2, sol_prov):
        """Calcula los costos de permutacion de dos trafos en una solucion provisional respecto a una solucion inicial.

        Args:
            id_t1 (int): id del trafo 1.
            id_t2 (int): id del trafo 2.
            sol_prov (tupla): solucion provisional de la red, asumiendo que la permutacion se realizo.

        Returns:
            cperm_t1 (float): costo de permutar el trafo 1, en pesos.
            cdete_t1 (float): costo de deterioro del trafo 1, en pesos.
            cperm_t2 (float): costo de permutar el trafo 2, en pesos.
            cdete_t1 (float): costo de deterioro del trafo 2, en pesos.
        
        """
        cperm_t1 = 0
        cperm_t2 = 0

        # para el trafo 1
        id_n1_orig = int(self.solini[(self.solini.id_t == id_t1)]['id_n'])
        id_n1_prov = int(sol_prov[(sol_prov.id_t == id_t1)]['id_n'])
        if id_n1_orig != id_n1_prov:
            cperm_t1 = self.costopermtf(id_t1)
            cdete_t1 = self.costodetetf(id_t1)

        # para el trafo 2
        id_n2_orig = int(self.solini[(self.solini.id_t == id_t2)]['id_n'])
        id_n2_prov = int(sol_prov[(sol_prov.id_t == id_t2)]['id_n'])
        if id_n2_orig != id_n2_prov:
            cperm_t2 = self.costopermtf(id_t2)
            cdete_t2 = self.costodetetf(id_t2)
        return (cperm_t1, cdete_t1, cperm_t2, cdete_t2)
    
    
    def condparada(self, sol):
        """Verifica si se ha cumplido la condición de parada de las permutaciones.
        
        Args:
            sol (tupla): solucion actual de la red.

        Returns:
            condstop (int): 1: se debe par, 0: se debe continuar.

        """
        condstop = 0
        #Seleccionar los nodos potenciales
        sol = sol.loc[(sol['eval'] == 0)]
        sol = sol.loc[(sol['bloq'] == 0)]
        sol = sol.loc[(sol['coper'] > 0)]
        if sol.shape[0] == 0: condstop = 1
        return condstop


    def bodega(self):
        """Calcula la bodega.
        """
        self.bodini = self.solini[self.solini.id_n == 999999]
        self.bodfin = self.solfin[self.solfin.id_n == 999999]
        tf_bodini = self.bodini.shape[0]
        tf_bodfin = self.bodfin.shape[0]
        cp_bodini = self.bodini['capa_t'].sum()
        cp_bodfin = self.bodfin['capa_t'].sum()

    
    def armarsolorig(self):
        """Arma la solucion actual de la red con sus costos asociados.
        """
        solorigi = pd.DataFrame(columns=['id_n','id_t','cpt','cvu','coper','cperm','cdete','eval','perm','bloq'])

        for index, row in self.inv.iterrows():
            id_n = int(row['id_n'])
            id_t = int(row['id_t'])

            # calculos de costos para los nodos reales y en bodega
            cpt_nt = 0
            cvu_nt = 0
            if id_n != 999999: 
                cpt_nt = self.cospt (id_n,id_t)
                cvu_nt = self.cospv (id_n,id_t)
            coper_nt = cpt_nt + cvu_nt              

            # almacenar el costo para ese arreglo en particular
            solorigi.loc[index]= [id_n,id_t,cpt_nt,cvu_nt,coper_nt,0,0,0,0,0]

        # poner carga maxima de nodos y capacidades de trafos en la solucion inicial
        solorigi = solorigi.merge(self.inv[['id_t','capa_t']], on = 'id_t',how = 'left')
        solorigi = solorigi.merge(self.nodos[['id_n','cmax_n']], on = 'id_n',how = 'left')

        # escribir la solucion inicial y calcular su costo
        solorigi.to_csv(self.pathoutput + 'solucion_inicial.csv')
        self.solini = solorigi.copy() 
        self.ctsolini = solorigi['coper'].sum()



    def permutar(self, sol):
        """Hace una permutacion de un par de trafos en una solucion y encuentra los costos asociados.
        
        Args:
            sol (tupla): solucion actual de la red.

        """

        # elegir el nodo mas costoso y el trafo mas costoso que se le adecua
        id_n1, id_t1, id_n2, id_t2 = self.hallarparejasperm(sol)
        sol.at[sol.id_n == id_n1,'eval'] = 1

        # calcular los costos de operacion actuales en los dos nodos
        coact_n1 = 0
        coact_n2 = 0
        if id_n1 != 999999: coact_n1 = float(sol[sol.id_n == id_n1]['coper'])
        if id_n2 != 999999: coact_n2 = float(sol[sol.id_n == id_n2]['coper'])
        coact = coact_n1 + coact_n2

        # calcular los costos de operacion despues de la permutacion en los dos nodos
        cpt_n1t2 = self.cospt(id_n1,id_t2)
        cvu_n1t2 = self.cospv (id_n1,id_t2)
        cpt_n2t1 = self.cospt(id_n2,id_t1)
        cvu_n2t1 = self.cospv (id_n2,id_t1)
        coper_n1 = cpt_n1t2 + cvu_n1t2
        coper_n2 = cpt_n2t1 + cvu_n2t1
        coper = coper_n1 + coper_n2

        # calcular los costos de permutacion de los transformadores
        sol_prov = sol.copy()
        sol_prov.at[(sol.id_n == id_n1) & (sol.id_t == id_t1),'id_t']=id_t2
        sol_prov.at[(sol.id_n == id_n2) & (sol.id_t == id_t2),'id_t']=id_t1
        cperm_t1,cdete_t1,cperm_t2,cdete_t2 = self.cospermpar(id_t1,id_t2,sol_prov)
        cperm = cperm_t1 + cperm_t2
        cdeter = cdete_t1 + cdete_t2

        
        # hacer el cambio oficial en la solucion
        self.per_hecha = 0
        if coact >= (coper + cperm + cdeter):
            self.per_hecha = 1

            # traer las capacidades
            capa_t1 = self.partf(id_t1)[0]
            capa_t2 = self.partf(id_t2)[0]

            #Actualizar la matriz de solución
            sol.at[(sol.id_n == id_n1) & (sol.id_t == id_t1),'id_t']=id_t2
            sol.at[(sol.id_n == id_n2) & (sol.id_t == id_t2),'id_t']=id_t1
            
            sol.at[(sol.id_n == id_n1) & (sol.id_t == id_t2),'cpt']=cpt_n1t2
            sol.at[(sol.id_n == id_n2) & (sol.id_t == id_t1),'cpt']=cpt_n2t1
            sol.at[(sol.id_n == id_n1) & (sol.id_t == id_t2),'cvu']=cvu_n1t2
            sol.at[(sol.id_n == id_n2) & (sol.id_t == id_t1),'cvu']=cvu_n2t1
            sol['coper'] = sol['cpt'] + sol['cvu']

            sol.at[(sol.id_n == id_n1) & (sol.id_t == id_t2),'cperm']=cperm_t2
            sol.at[(sol.id_n == id_n2) & (sol.id_t == id_t1),'cperm']=cperm_t1
            sol.at[(sol.id_n == id_n1) & (sol.id_t == id_t2),'cdete']=cdete_t2
            sol.at[(sol.id_n == id_n2) & (sol.id_t == id_t1),'cdete']=cdete_t1
            sol.at[(sol.id_n == id_n1) & (sol.id_t == id_t2),'capa_t']=capa_t2
            sol.at[(sol.id_n == id_n2) & (sol.id_t == id_t1),'capa_t']=capa_t1
            sol.at[(sol.id_t == id_t1),'perm']=1
            sol.at[(sol.id_t == id_t2),'perm']=1

        #Guardar estadísticas
        self.solfin = sol.copy() 
        self.cosolfin = sol['coper'].sum()
        self.cpsolfin = sol['cperm'].sum()
        self.cdsolfin = sol['cdete'].sum()
        self.ctsolfin = self.cosolfin + self.cpsolfin + self.cdsolfin
        

        
    def run(self):
        """Ejecuta la rutina de optimizacion.
        """

        self.set_working_dir(working_dir="../Tests/Test1/")
        self.load_data()
        self.armarsolorig()
        
        # armar la matriz de progresos en el hallazgo de mejores soluciones
        self.prog_sol = pd.DataFrame(columns=['iteracion','tperm','coper','cperm','cdete','costo_total'])
        self.prog_sol.loc[0] = [0,0,self.ctsolini,0,0,self.ctsolini]
        
        # inicializar contadores y condicion de parada
        titer = 0
        tperm = 0
        sol = self.solini.copy()
        stop = self.condparada(sol)
        
        # iterar
        while (stop == 0):
            # permutar
            self.permutar(sol)

            # actualizar contadores
            tperm = tperm + self.per_hecha
            titer = titer + 1

            # guardar progreso de la simulacion
            self.prog_sol.loc[titer] = [titer,tperm,self.cosolfin,self.cpsolfin,self.cdsolfin,self.ctsolfin]     

            # verificar condicion de parada
            stop = self.condparada(sol)

        # exportar los resultados de la solucion final
        self.bodega()
        self.solfin.to_csv(self.pathoutput + 'solucion_final.csv')
        self.prog_sol.to_csv(self.pathoutput + 'progreso_soluciones.csv')
        self.bodini.to_csv(self.pathoutput + 'bodega_inicial.csv')
        self.bodfin.to_csv(self.pathoutput + 'bodega_final.csv')

        
if __name__ == "__main__":
    import doctest
    doctest.testmod()


# In[3]:


m = Optimizer()
m.run()


# In[4]:


print(m.ctsolini)
print(m.ctsolfin)

