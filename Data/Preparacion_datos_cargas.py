
# coding: utf-8

# In[7]:


#get_ipython().run_line_magic('reset', '-f')

import numpy as np
import pandas as pd
import dateutil
import configparser


# In[8]:


def load_data():
    """Lee los datos del directorio de trabajo.
    """

    global pathoutput, data

    data = pd.read_csv(working_dir + "datos.csv", sep=',', decimal='.')


# In[9]:


def construircol():
    """Construye las columnas necesarias para el analisis.
    """

    global data

    data['Fecha'] = data['Fecha'].apply(dateutil.parser.parse, dayfirst=True)
    data['ano'] = pd.DatetimeIndex(data['Fecha']).year
    data['mes'] = pd.DatetimeIndex(data['Fecha']).month
    data['dia'] = pd.DatetimeIndex(data['Fecha']).day
    data['hora'] = pd.DatetimeIndex(data['Fecha']).hour
    data['minuto'] = pd.DatetimeIndex(data['Fecha']).minute
    data = data.sort_values(['ID_Transformador', 'Fecha'], ascending=[True, True])
    data['carga'] = data['Energia_Activa_kWh'] - data['Energia_Activa_kWh'].shift(1)
    data.loc[(data.carga < 0), 'carga'] = np.nan
    data.loc[(data.hora != data.hora.shift(1)) & (data.hora - 1 != data.hora.shift(1)), 'carga'] = np.nan
    data.loc[(data.dia != data.dia.shift(1)) & (data.dia - 1 != data.dia.shift(1)), 'carga'] = np.nan


# In[10]:


def removout():
    """Remueve los outliers de la columna carga, por transformador.
    Los outliers se presentan por inconsistencias en la informacion.
    Outlier: dato que esta a mas de 2.5 desviaciones estandar de la media.

    """

    global data

    grupos = data.groupby(['ID_Transformador'])
    prov = pd.DataFrame(grupos['carga'].mean())
    prov['LS'] = grupos['carga'].mean() + grupos['carga'].std() * 2.5
    prov['LI'] = grupos['carga'].mean() - grupos['carga'].std() * 2.5
    prov['id_t'] = prov.index
    data = data.rename(columns={'ID_Transformador': 'id_t'})
    data = data.merge(prov[['LS','LI','id_t']], on = 'id_t',how='right')
    data.loc[(data.carga >= data.LS) | (data.carga <= data.LI), 'carga'] = np.nan


# In[11]:


def cmaxpromdia():
    """Calcula la carga maxima de cada nodo por dia, como la maxima de las cargas consolidadas por hora.
    Calcula la carga promedio de cada nodo por dia, como el promedio de las cargas consolidadas por hora.

    """

    global c_max_prom_dia

    grupos1 = data.groupby(['id_t','ano','mes','dia','hora'])
    prov1 = pd.DataFrame(grupos1['carga'].sum())

    grupos2 = prov1.groupby(['id_t','ano','mes','dia'])
    c_max_prom_dia = pd.DataFrame(grupos2['carga'].max())
    c_max_prom_dia['cmax'] = grupos2['carga'].max()
    c_max_prom_dia['cpro'] = grupos2['carga'].mean()


# In[12]:


def cmaxpromnodo():
    """Calcula la carga maxima de cada nodo, como el promedio de las cargas maximas por dia.
    Calcula la carga promedio de cada nodo, como el promedio de las cargas promedio por dia.

    """

    global c_max_prom_nodo

    grupos = c_max_prom_dia.groupby(['id_t','ano'])
    c_max_prom_nodo = pd.DataFrame(grupos['cmax'].max())
    c_max_prom_nodo['cmax'] = grupos['cmax'].mean()
    c_max_prom_nodo['prom'] = grupos['cpro'].mean()


# In[13]:


def ddapromnodo():
    """Calcula la demanda promedio de cada nodo, como el promedio de las demandas por dia.

    """

    global d_prom_nodo

    grupos = data.groupby(['id_t','ano','mes','dia'])
    prov = pd.DataFrame(grupos['carga'].sum())
    prov['horas_med'] = ((grupos['Fecha'].max() - grupos['Fecha'].min()).dt.total_seconds())/(60*60)
    prov['dda_med'] = grupos['Energia_Activa_kWh'].max() - grupos['Energia_Activa_kWh'].min()
    prov['dda_dia'] = prov['dda_med'] / prov['horas_med'] * 24

    grupos1 = prov.groupby(['id_t','ano'])
    d_prom_nodo = pd.DataFrame(grupos1['dda_dia'].mean())
    d_prom_nodo.index.names = ['id_tf','ano']
    d_prom_nodo['id_t'] = d_prom_nodo.index.get_level_values('id_tf')


# In[14]:


def cydpornodo():
    """Consolida la informacion de carga promedio, carga maxima y demanda por nodo.

    """
    global cyd_pornodo

    cmaxpromdia()
    cmaxpromnodo()
    ddapromnodo()
    cyd_pornodo = c_max_prom_nodo.merge(d_prom_nodo[['dda_dia','id_t']], on = 'id_t',how='right')


# In[15]:


#Ejecuta la simulacion

working_dir=""
load_data()
construircol()
removout()
cydpornodo()

# reporte en csv
data.to_csv(working_dir + 'data.csv')
cyd_pornodo.to_csv(working_dir + 'cyd_pornodo.csv')
