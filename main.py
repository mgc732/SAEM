# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 10:42:10 2023

"""
from sqlalchemy import func, inspect
from modulos.declarative_base import Session, engine, Base
from modulos.region import Region
from modulos.imagen import Imagen
from modulos.paciente import Paciente
from modulos.voxel import Voxel
from modulos.metabolito import Metabolito

import tkinter as tk
from tkinter import filedialog, ttk, Menu, messagebox as msg 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # permite mostrar los gráficos generados por 
                                                                # matplotlib dentro de una ventana o marco de 
                                                                # tkinter
import seaborn as sns

from PIL import Image, ImageTk # La biblioteca Pillow proporciona un conjunto de herramientas poderosas para 
                               # trabajar con imágenes en Python, permitiendo abrir, manipular, guardar y mostrar 
                               # imágenes en diferentes formatos
import pydicom

import numpy as np
import re
import sys
import pandas as pd

# Variables globales
filas = 0
columnas = 0
ventana_matriz = None
letra = 11
df = pd.DataFrame()

#--------------------------------------------------------------
def cargar_bd(cabecera, matriz_region, imagen_recortada):
    """
    Carga la información de un paciente y su imagen a la base de datos.

    Args:
        cabecera (dict): Un diccionario que contiene la información de la cabecera del paciente y la imagen.
            Debe incluir las siguientes claves:
                - 'id': Identificador del paciente (int).
                - 'nombre': Nombre del paciente (str).
                - 'apellido': Apellido del paciente (str).
                - 'edad': Edad del paciente (int).
                - 'genero': Género del paciente (str).
                - 'imagen': Nombre de la imagen (str).
                - 'fecha': Fecha de la imagen (str).
                - 'metabolito': Nombre del metabolito (str).
        matriz_region (list): Una matriz representando las regiones de la imagen.
            Debe ser una lista de listas de enteros.
        imagen_recortada (list): Una matriz con los valores de los píxeles de la imagen recortada.
            Debe ser una lista de listas de valores numéricos.

    Note:
        La función realiza las siguientes acciones:
        - Crea la base de datos si no existe.
        - Agrega las regiones predefinidas en la base de datos.
        - Agrega un paciente y su información si no existe.
        - Agrega una imagen y sus voxels si no existe.
        - Agrega un voxel y su metabolito si no existe.

    Returns:
        None
    """
    matriz_region = np.array(matriz_region)
    if np.any(matriz_region != 0) and cabecera['edad']>=18:
        #Crea la BD
        Base.metadata.create_all(engine)
        #Abre la sesión
        session = Session()
        #Regiones 
        regiones = []
        regiones.append(Region(id=1, nombre='parietal'))
        regiones.append(Region(id=2, nombre='frontal'))
        regiones.append(Region(id=3, nombre='occipital'))
        regiones.append(Region(id=4, nombre='temporal'))
        regiones.append(Region(id=5, nombre='nucleo'))
        
        for region in regiones:
            region_bd = session.get(Region, region.id)
            # Verificar si el objeto existe en la base de datos
            if region_bd is None:
                session.add(region)
                msg.showinfo('Base de datos','Agregada nueva Región')
        paciente_mem = Paciente(cabecera['id'], 
                                cabecera['nombre'],
                                cabecera['apellido'], 
                                cabecera['edad'], 
                                cabecera['genero'])
        
        
        paciente_bd = session.query(Paciente).filter_by(id=paciente_mem.id).first() 
        
        # Si no existe el paciente, lo agrego
        if paciente_bd is None:
            imagen_mem = Imagen(cabecera['imagen'], cabecera['fecha'])
            #session.add(paciente)
            #imagen = Imagen(nombre=cabecera['imagen'], fecha =cabecera['fecha'], paciente=paciente)
            #session.add(imagen)
            #paciente.imagenes.append(imagen)
            for i in range(len(matriz_region)):
                for j in range(len(matriz_region[0])):
                    if matriz_region[i][j]!=0:
                        metabolito = Metabolito(cabecera['metabolito'], imagen_recortada[i][j])
                        #session.add(metabolito)
                        voxel = Voxel(i, j)
                        #session.add(voxel)
                        voxel.region = session.get(Region, int(matriz_region[i][j]))
                        voxel.metabolitos.append(metabolito)
                        #metabolito.voxel = voxel
                        imagen_mem.voxeles.append(voxel)
            paciente_mem.imagenes.append(imagen_mem)
            session.add(paciente_mem)
            #print('Registro agregado(1)')
            msg.showinfo('Base de datos',f'Agregado Paciente:\n\t* id:{paciente_mem.id}\n\t* Imagen\n\t* Metabolito') 

        # Si existe el paciente pero no existe la imagen, la agrego
        elif (cabecera['imagen'], cabecera['fecha']) not in [(ima.nombre, ima.fecha) for ima in paciente_bd.imagenes]:
            imagen_mem = Imagen(cabecera['imagen'], cabecera['fecha'])
            #paciente = session.merge(paciente)
            #imagen = Imagen(nombre=cabecera['imagen'], fecha =cabecera['fecha'], paciente=paciente)
            #session.add(imagen)
            #paciente.imagenes.append(imagen)
            for i in range(len(matriz_region)):
                for j in range(len(matriz_region[0])):
                    if matriz_region[i][j]!=0:
                        metabolito = Metabolito(cabecera['metabolito'], imagen_recortada[i][j])
                        #session.add(metabolito)
                        voxel = Voxel(i, j)
                        #session.add(voxel)
                        voxel.region = session.get(Region, int(matriz_region[i][j]))
                        voxel.metabolitos.append(metabolito)
                        #metabolito.voxel = voxel
                        imagen_mem.voxeles.append(voxel)
            paciente_bd.imagenes.append(imagen_mem)
            #print('Registro agregado (2)')
            msg.showinfo('Base de datos', f'Agregada:\n\t* Imagen\n\t* Metabolito\nAsociada al Paciente id:{paciente_bd.id}') 

        else:
            indice = 0 
            for i, imagen in enumerate(paciente_bd.imagenes):
                #print(imagen.nombre, imagen.fecha)
                if (imagen.nombre, imagen.fecha) == (cabecera['imagen'], cabecera['fecha']):
                   # print(imagen.nombre, imagen.fecha)
                   # print(cabecera['imagen'], cabecera['fecha'])
                    indice = i
                    break
            else:
                #print(cabecera['imagen'], cabecera['fecha'])
                msg.showerror('Base de datos', 'No se encontro la imagen')
            imagen_bd = paciente_bd.imagenes[indice]
            lista_tuplas = [(i, j) for i in range(len(matriz_region)) for j in range(len(matriz_region[0])) if matriz_region[i][j]!=0]
            #print(lista_tuplas)
            for tupla in lista_tuplas:
                voxel = Voxel(tupla[0], tupla[1])
                voxel.region = session.get(Region, int(matriz_region[tupla[0]][tupla[1]]))
                if voxel not in imagen_bd.voxeles:
                    metabolito = Metabolito(cabecera['metabolito'], imagen_recortada[tupla[0]][tupla[1]])
                    voxel.metabolitos.append(metabolito)
                    imagen_bd.voxeles.append(voxel)
                    msg.showinfo('Base de datos', f'Agregado Voxel\nAsociado a:\n\t* Paciente id:{paciente_bd.id}\n\t* imagen id:{imagen_bd.id}')
                else:
                    vox_bd = imagen_bd.voxeles[imagen_bd.voxeles.index(voxel)]                                                        
                    if cabecera['metabolito'] not in [meta.nombre for meta in vox_bd.metabolitos] and vox_bd.region_id == int(matriz_region[tupla[0]][tupla[1]]):
                        #print(vox_bd.region_id, int(matriz_region[tupla[0]][tupla[1]]))
                        metabolito = Metabolito(cabecera['metabolito'],  imagen_recortada[tupla[0]][tupla[1]])
                        vox_bd.metabolitos.append(metabolito)
                        msg.showinfo('Base de datos', 
                                     f'Agregado Metabolito\nAsociado a:\n\t* Paciente id:{paciente_bd.id}\n\t* Imagen id:{imagen_bd.id}\n\t* Voxel id:{vox_bd.id}')
                    else:
                        msg.showwarning('Base de datos', 'Compruebe los datos')

      
        session.commit()
        session.close()
    else:
        if np.all(matriz_region == 0):
            msg.showerror('Base de datos', 'Regiones vacía') 
        else:
            msg.showerror('Base de datos', 'Restricción de edad\nEl paciente es menor de edad')  

def get_region(filas, columnas, cabecera, imagen_recortada):
    """ obtiene información en una matriz de regiones y llama a la función 'cargar_bd' para cargarla en una base de datos.
    Parámetros:
        filas (int): Número de filas en la matriz de regiones.
        columnas (int): Número de columnas en la matriz de regiones.
        cabecera (dict): Un diccionario que contiene información de la cabecera, incluyendo:
            - 'id' (int): ID del paciente.
            - 'nombre' (str): Nombre del paciente.
            - 'apellido' (str): Apellido del paciente.
            - 'edad' (int): Edad del paciente.
            - 'genero' (str): Género del paciente.
            - 'imagen' (str): Nombre de la imagen.
            - 'fecha' (str): Fecha de la imagen.
            - 'metabolito' (str): Nombre del metabolito.
        imagen_recortada (list): Una matriz (lista de listas) que representa la imagen recortada.
    Notas:
        - La función crea una matriz de regiones y la llena según los valores proporcionados en 'matriz_entries'.
        - Llama a la función 'cargar_bd' para guardar la información en una base de datos.
        - Cierra las ventanas 'ventana_matriz' y 'ventana_fig' al guardar la información.
    """
    matriz_region = [[0]*columnas for i in range(filas)]
    for i in range(filas):
        for j in range(columnas):
            if not matriz_entries[i][j].get()=='':
                if matriz_entries[i][j].get() == 'parietal':
                    matriz_region[i][j] = 1
                elif matriz_entries[i][j].get() == 'frontal':
                    matriz_region[i][j] = 2
                elif matriz_entries[i][j].get() == 'occipital':
                    matriz_region[i][j] = 3
                elif matriz_entries[i][j].get() == 'temporal':
                    matriz_region[i][j] = 4
                else:
                    matriz_region[i][j] = 5
            
    ventana_matriz.destroy()  # Cerrar la ventana de la matriz al guardar
    ventana_fig.destroy()
    cargar_bd(cabecera, matriz_region, imagen_recortada)

def get_color_por_valor(valor, vmin, vmax, colormap='viridis'):
    """
    Obtener el color correspondiente a un valor dentro de un rango específico utilizando una paleta de colores.
    Parámetros:
    valor (float): El valor para el cual se obtendrá el color.
    vmin (float): Valor mínimo del rango.
    vmax (float): Valor máximo del rango.
    colormap (str): Nombre de la paleta de colores a utilizar. El valor predeterminado es 'viridis'.
    Retorna:
    str: El código hexadecimal de color en formato '#rrggbb'.
    """
    '''
    norm_valor = (valor - vmin) / (vmax - vmin)
    cmap = plt.get_cmap(colormap)
    rgba = cmap(norm_valor)
    #rgba = get_rgba(norm_valor)
    r = int(rgba[0] * 255)
    g = int(rgba[1] * 255)
    b = int(rgba[2] * 255)
    return f'#{r:02x}{g:02x}{b:02x}'
    '''
    norm_valor = (valor - vmin) / (vmax - vmin)
    gray_value = int(norm_valor * 255)
    return f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'

def generar_ventana_matriz_regiones(filas, columnas, cabecera, imagen_recortada):
    """ Crea una ventana emergente para relacionar regiones con los voxeles de la imagen.
    Parámetros:
        filas (int): Número de filas en la matriz de regiones.
        columnas (int): Número de columnas en la matriz de regiones.
        cabecera (dict): Un diccionario que contiene información de la cabecera, incluyendo:
            - 'id' (int): ID del paciente.
            - 'nombre' (str): Nombre del paciente.
            - 'apellido' (str): Apellido del paciente.
            - 'edad' (int): Edad del paciente.
            - 'genero' (str): Género del paciente.
            - 'imagen' (str): Nombre de la imagen.
            - 'fecha' (str): Fecha de la imagen.
            - 'metabolito' (str): Nombre del metabolito.
        imagen_recortada (list): Una matriz (lista de listas) que representa la imagen recortada.
    Notas:
        - La función crea una ventana emergente (Toplevel) para ingresar las regiones en una matriz.
        - Cada celda de la matriz contiene un Combobox con opciones para seleccionar la región.
        - Se utiliza la variable global 'ventana_matriz' para mantener una referencia a la ventana emergente.
        - Se utiliza la variable global 'matriz_entries' para mantener una referencia a los Combobox creados.
        - Al hacer clic en el botón 'Guardar', llama a la función 'get_region' para guardar la información 
          en una base de datos.
    """
    global ventana_matriz
    global matriz_entries
    
    ventana_matriz = tk.Toplevel(root)
    ventana_matriz.title("Regiones")
    matriz_entries = []
    opciones = ['','parietal', 'frontal', 'occipital', 'temporal', 'nucleo']  # Lista de opciones para el Combobox
    for i in range(0,filas*2,2):
        fila_entries = []
        for j in range(columnas):
            # Crear el Combobox en la primera celda
            combo = ttk.Combobox(ventana_matriz,
                                 state="readonly",
                                 values=opciones,
                                 width=8, 
                                 )
            combo.current(0)  # Seleccionar la primera opción por defecto
            combo.grid(row=i, column=j, padx=2)
            fila_entries.append(combo)
            
        matriz_entries.append(fila_entries)
        #ventana_matriz.rowconfigure(i, minsize=30)
    ind=0
    for i in range(1,filas*2+1,2):
        #ventana_matriz.rowconfigure(i, minsize=30)
        for j in range(columnas):
            canvas = tk.Canvas(ventana_matriz,
                               width=70,
                               height=60, 
                               highlightthickness=0, 
                               bg=get_color_por_valor(imagen_recortada[ind][j], 
                               np.min(imagen_recortada),
                               np.max(imagen_recortada), colormap='viridis'))
            canvas.grid(row=i, column=j, padx=2, pady=2)
        ind+=1        
    
    btn_cargar = ttk.Button(ventana_matriz, text="Cargar", command=lambda: get_region(filas, columnas, cabecera, imagen_recortada))
    btn_cargar.grid(row=filas*2+2, columnspan=columnas, pady=10)
    ventana_matriz.resizable(False, False)
  
def generar_ventana_figura(image):
    """ Genera una ventana emergente que muestra una imagen utilizando Matplotlib y Tkinter.
    Parámetros:
        image (numpy.ndarray): La imagen a mostrar. Debe ser un arreglo de NumPy.
    Notas:
        - La función crea una ventana emergente (Toplevel) para mostrar la imagen.
        - Utiliza Matplotlib para crear y mostrar la imagen dentro de la ventana emergente.
        - Se utiliza la variable global 'ventana_fig' para mantener una referencia a la ventana emergente.
        - La imagen se muestra en escala de grises (cmap=plt.cm.gray) y sin ejes (plt.axis('off')).
        - La ventana emergente no es redimensionable.
    """
    global ventana_fig
    ventana_fig = tk.Toplevel(root)
    ventana_fig.title("Imagen")
    # Mostrar la imagen recortada en la ventana de la matriz
    fig = plt.figure(figsize=(4, 4))
    ax1 = fig.add_subplot(111)
    pos = ax1.imshow(image, cmap='gray')
    ax1.axis('off')
    ax1.set_title('Imagen DICOM recortada')
    # Agregar el colorbar a la figura
    fig.colorbar(pos, ax=ax1)
   
    canvas = FigureCanvasTkAgg(fig, master=ventana_fig)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    ventana_fig.resizable(False, False)
#-------------------------------------------------------------------------------------------
def cargar_archivo():
    """ Carga un archivo DICOM, accede a los metadatos y datos del archivo, y muestra la imagen en una ventana
        emergente.
    Notas:
        - La función abre una ventana de diálogo para que el usuario seleccione un archivo DICOM.
        - Accede a los metadatos y datos del archivo DICOM utilizando PyDICOM.
        - Muestra la imagen en una ventana emergente utilizando la función 'generar_ventana_figura'.
        - Si la imagen contiene datos válidos, se recorta la matriz de la imagen y se crea una ventana emergente 
          para ingresar texto (matriz de regiones).
        - Actualiza el estado de los widgets 'label_carga_exitosa' y 'label_base' según el resultado de la carga 
          del archivo.
    """
    if ventana_matriz!= None:
        ventana_matriz.destroy()
        ventana_fig.destroy()
    
    # Abrir ventana de diálogo para seleccionar el archivo
    file_path = filedialog.askopenfilename()
    if file_path:
        # Cerrar la ventana de información del paciente si existe
        #if ventana_info_paciente is not None:
        #    ventana_info_paciente.destroy()

        # Cargar el archivo DICOM
        dataset = pydicom.dcmread(file_path)

        if (0x0051, 0x1002) in dataset:
            # Acceder al valor correspondiente
            metabolito = dataset[(0x0051, 0x1002)].value
        else:
            metabolito = ''

          # Acceder a los metadatos y datos del archivo DICOM
        fecha = dataset.AcquisitionDate
        fecha = fecha[0:4]+'-'+fecha[4:6]+'-'+fecha[6:]
        cabecera = {
            'id': dataset.PatientID,
            'nombre': dataset.PatientName.given_name,
            'apellido': dataset.PatientName.family_name,
            'genero': dataset.PatientSex,
            'edad': int(re.sub('^0+', '', re.sub('[^\d]', '', dataset.PatientAge))),
            'fecha': fecha,
            'metabolito': metabolito,
            'imagen' :  re.search(r"IM\d", file_path).group()
        }    
        cabecera_inf = '\n'.join([f'{x.capitalize()}: {y}' for x,y in cabecera.items()])
        # Acceder a los píxeles de la imagen (si es un archivo de imagen DICOM)
        rescale_slope = dataset[(0x0028, 0x1053)].value
        rescale_intercept = dataset[(0x0028, 0x1052)].value
        if 'PixelData' in dataset:
            # Obtener los valores de Rescale Slope y Rescale Intercept
            #print(rescale_intercept, rescale_slope)
            image = dataset.pixel_array
            # Aplicar la conversión automática utilizando los parámetros de Rescale Slope e Intercept
            image_ajustados = rescalado(image, rescale_slope, rescale_intercept)
            #print(image_ajustados)
            if not np.all(image_ajustados == 0):
                # Recortar la matriz utilizando los índices     
                filas_no_cero, columnas_no_cero = np.nonzero(image_ajustados)
                image_recortada = image_ajustados[min(filas_no_cero):max(filas_no_cero)+1, min(columnas_no_cero):max(columnas_no_cero)+1]
                filas = np.shape(image_recortada)[0]
                columnas = np.shape(image_recortada)[1]

                # Actualizar el label con el mensaje de carga exitosa del archivo
                msg.showinfo('Lectura exitosa del archivo DICOM', cabecera_inf)
                generar_ventana_matriz_regiones(filas, columnas, cabecera, image_recortada)
                generar_ventana_figura(image_recortada)
                
            else:
                # Actualizar el label con el mensaje de carga exitosa del archivo
                msg.showinfo('Lectura exitosa del archivo DICOM', '      No hay datos asociados a una imagen      ')
def rescalado(imagen, slope, intercept):
    '''Escalado de la imagen'''
    if intercept == 0:
        return imagen*slope
    else:
        msg.showerror('Rescale_intercept',  'Distinto de cero')
        return imagen

def procesamiento_bd(region_seleccionda):
    '''Realiza el procesamiento de datos en la base de datos para una región específica.
    Args:
        region_seleccionada (str): El nombre de la región seleccionada en minúsculas.
    Returns:
        None
    Description:
        Esta función realiza una consulta en la base de datos para obtener los promedios de concentración de metabolitos
        en la región seleccionada. Luego, calcula las proporciones de Naa/Cre y Cho/Cre. Si alguna de las divisiones por cero
        ocurre, imprime un mensaje de advertencia.
        Parameters:
            - region_seleccionada: El nombre de la región seleccionada en minúsculas, como 'parietal' o 'frontal'.
        Results:
        - Muestra en una interfaz gráfica las siguientes relaciones:
            * Relación de Naa/Cre
            * Relación de Cho/Cre
            * Suma de Creatina y Colina
            * Relación de Cho/Naa
            * Relación de Naa/Cho
            * Relación de Cre/Naa '''
    inspector = inspect(engine)
    if 'paciente' not in inspector.get_table_names():
        msg.showerror('Base de datos', 'Base de datos vacía')
        ventana_procesamiento.destroy()
    else:
        # Crear una sesión
        session = Session()

        if region_seleccionda!='':
            results = session.query(Metabolito.nombre,
                                    Metabolito.concentracion,
                                    Region.nombre,
                                    Paciente.id,
                                    Paciente.genero,
                                    Paciente.edad,
                                    Imagen.fecha
                                ).join(Voxel, Metabolito.voxel_id == Voxel.id)\
                                .join(Region, Voxel.region_id == Region.id)\
                                .join(Imagen, Voxel.imagen_id == Imagen.id)\
                                .join(Paciente, Imagen.paciente_id == Paciente.id)\
                                .filter(Region.nombre == region_seleccionda.lower())\
                                .all()

        # Cerrar la sesión
        session.close()

        # Crear el DataFrame a partir de los resultados de la consulta
        global df
        df = pd.DataFrame(results, columns=[
            'nombre_metabolito',
            'concentracion',
            'region',
            'id_paciente',
            'genero',
            'edad',
            'fecha_imagen'
        ])
        # Calcular la mediana de 'concentracion' para cada 'id_paciente' y 'nombre_metabolito'
        medianas = df.groupby(['id_paciente', 'nombre_metabolito'])['concentracion'].median()

        # Reemplazar todos los valores de concentración con las medianas correspondientes
        df['concentracion'] = df.set_index(['id_paciente', 'nombre_metabolito']).index.map(medianas)

        # Eliminar las filas duplicadas en función de 'id_paciente' y 'nombre_metabolito'
        df.drop_duplicates(subset=['id_paciente', 'nombre_metabolito'], keep='first', inplace=True)
        #pd.set_option('display.max_columns', None)
        #print(df.describe())
        # Imprimir el DataFrame (opcional)
        if not df.empty:
            # Calcular las proporciones de Naa/Cre y Cho/Cre
            ratios = df.pivot_table(index='id_paciente', columns='nombre_metabolito', values='concentracion', aggfunc='first')
            
            try:
                ratios['N-Acetyl/Creatine'] = ratios['N-Acetyl'] / ratios['Creatine']
                ratios['Choline/Creatine'] = ratios['Choline'] / ratios['Creatine']
                ratios['Creatine/Choline'] = ratios['Creatine'] / ratios['Choline']
                ratios['Choline/N-Acetyl'] = ratios['Choline'] / ratios['N-Acetyl']
                ratios['N-Acetyl/Choline'] = ratios['N-Acetyl'] / ratios['Choline']
                ratios['Creatine/N-Acetyl'] = ratios['Creatine'] / ratios['N-Acetyl']
                df = pd.merge(df, ratios, left_on='id_paciente', right_on='id_paciente')
                df.drop_duplicates(subset=['id_paciente'], keep='first', inplace=True)

                #print(df.describe())
            except ZeroDivisionError:
                # En caso de división por cero, asignar valor predeterminado
                ratios['N-Acetyl/Creatine'] = -1
                ratios['Choline/Creatine'] = -1
                ratios['Creatine/Choline'] = -1
                ratios['Choline/N-Acetyl'] = -1
                ratios['N-Acetyl/Choline'] = -1
                ratios['Creatine/N-Acetyl'] = -1

            # Grafico de dispersion con jitter y diferenciado por genero usando lmplot
            '''
            sns.lmplot(data=df, x='edad', y='N-Acetyl/Creatine', hue='genero', scatter_kws={'alpha': 0.5, 's': 30}, x_jitter=True)
            plt.xlabel('Edad')
            plt.ylabel('N-Acetyl/Creatine')
            plt.title('Gráfico de dispersión con línea de tendencia por género')
            plt.show()'''
            # Crear etiquetas para mostrar las proporciones
            tk.Label(frame_region, text=f" Relación de Naa/Cre ==> Valor Ref: {ratios['N-Acetyl/Creatine'].mean():.3f} ",
                    font=f'Helvetica {letra} bold').grid(row=2, column=2, sticky='W')
            tk.Label(frame_region, text=f" Relación de Cho/Cre ==> Valor Ref:  {ratios['Choline/Creatine'].mean():.3f} ",
                    font=f'Helvetica {letra} bold').grid(row=3, column=2, sticky='W')
            tk.Label(frame_region, text=f" Creatine + Choline    ==> Valor Ref:  {(ratios['Creatine']+ratios['Choline']).mean():.1f} ",
                    font=f'Helvetica {letra} bold').grid(row=4, column=2, sticky='W')
            tk.Label(frame_region, text=f" Relación de Cho/Naa ==> Valor Ref:  {ratios['Choline/N-Acetyl'].mean():.3f} ",
                    font=f'Helvetica {letra} bold').grid(row=5, column=2, sticky='W')
            tk.Label(frame_region, text=f" Relación de Naa/Cho ==> Valor Ref:  {ratios['N-Acetyl/Choline'].mean():.3f} ",
                    font=f'Helvetica {letra} bold').grid(row=6, column=2, sticky='W')
            tk.Label(frame_region, text=f" Relación de Cre/Naa  ==> Valor Ref:  {ratios['Creatine/N-Acetyl'].mean():.3f} ",
                    font=f'Helvetica {letra} bold').grid(row=7, column=2, sticky='W')
            
        else:
            # Si el DataFrame está vacío, mostrar un mensaje de advertencia
            msg.showwarning("Advertencia", "No hay elementos para procesar.")

def generar_ventana_de_procesamiento():
    '''Crea y muestra una nueva ventana para el procesamiento de datos.
    
    Esta función crea una ventana de procesamiento utilizando la biblioteca Tkinter
    para la interfaz gráfica. La ventana incluye opciones para exportar datos a un
    archivo CSV y para salir de la aplicación. También contiene un selector de región
    en un Combobox que permite al usuario elegir una región específica para el procesamiento
    de datos. Cuando se selecciona una región, se activa una función de procesamiento de base
    de datos para llevar a cabo la tarea correspondiente.

    Args:
        None

    Returns:
        None
    '''
    # Crear una nueva ventana
    global ventana_procesamiento
    global frame_region

    ventana_procesamiento = tk.Toplevel(root)
    ventana_procesamiento.title("Procesamiento")
    menu_procesamiento = Menu(ventana_procesamiento)
    ventana_procesamiento.config(menu=menu_procesamiento)
    file = Menu(menu_procesamiento, tearoff=0)
    file.add_command(label='Export a csv', command=exportar_csv)
    file.add_separator()
    file.add_command(label='Salir', command=terminar_root)
    menu_procesamiento.add_cascade(label='File', menu=file)
    #agregando items

    
    frame_region = ttk.LabelFrame(ventana_procesamiento, text='Región')
    frame_region.grid(column=2, row=0, padx=20, pady=20)
    # Label using mighty as the parent 
    a_label = tk.Label(frame_region, text="Selector de Región")
    a_label.grid(column=0, row=0, sticky='W')
     
    opciones = ['','Parietal', 'Frontal', 'Occipital', 'Temporal', 'Nucleo']  # Lista de opciones para el Combobox
    combo = ttk.Combobox(frame_region,
                         state="readonly",
                         values=opciones,
                         width=9, 
                         )
    #Posicion dentro de la ventana
    combo.grid(row=0, column=1, padx=2)
      
    # Evento selector => llamada a procesamiento
    combo.bind("<<ComboboxSelected>>", lambda _:procesamiento_bd(combo.get()))
    ventana_procesamiento.resizable(False, False)

def exportar_csv():
    """
    Guarda datos y genera gráficos basados en un DataFrame.

    Esta función guarda los datos del DataFrame en un archivo CSV y genera gráficos
    de dispersión y mapas de calor basados en las correlaciones de las variables.

    Args:
        df (pandas.DataFrame): Un DataFrame que contiene los datos a guardar y graficar.

    Returns:
        None

    Note:
        Esta función guarda los datos en un archivo CSV y crea gráficos de dispersión y mapas de calor
        basados en las correlaciones de variables en el DataFrame. Los gráficos se guardan en la carpeta
        './data/'.

    Example:
        guardar_datos_y_graficos(datos_df)

    """

    if df.empty:
            msg.showwarning("Advertencia", "No hay elementos para guardar.")
    else:
        nombre_region = df['region'].iloc[0]
        nombre_archivo = f'./data/datos_metabolitos_{nombre_region}.csv'

        df_csv = df.drop(columns=['nombre_metabolito', 'concentracion'])
        '''
        df_correlaciones = df.drop(columns=['id_paciente',
                                            'nombre_metabolito',
                                            'concentracion',
                                            'region', 
                                            'fecha_imagen',
                                            'Choline',
                                            'N-Acetyl',
                                            'Creatine'])
        
        # Crear el gráfico de dispersión con líneas de tendencia
        g = sns.PairGrid(df_correlaciones, hue='genero')
        g.map_diag(sns.histplot)
        g.map_offdiag(sns.scatterplot)
        g.map_offdiag(sns.regplot, scatter_kws={'alpha':0.5})
        # Agregar una leyenda
        g.add_legend()
        # Guardar el gráfico como un archivo PDF
        plt.figure()
        g.savefig('./data/scatterplot_with_trendlines.pdf')
        # Calcular la matriz de correlación
        correlation_matrix = df.drop(columns=['id_paciente',
                                            'nombre_metabolito',
                                            'concentracion',
                                            'region', 
                                            'fecha_imagen',
                                            'Choline',
                                            'N-Acetyl',
                                            'Creatine',
                                            'genero']).corr()
        plt.figure()
        # Graficar la matriz de correlación
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
        plt.tight_layout()
        plt.savefig('./data/heatmap.pdf')
        
        correlation_with_age = df.drop(columns=['id_paciente',
                                            'nombre_metabolito',
                                            'concentracion',
                                            'region', 
                                            'fecha_imagen',
                                            'Choline',
                                            'N-Acetyl',
                                            'Creatine',
                                            'genero']).corr()['edad'].drop('edad')
        print(correlation_with_age)
        '''
        df_csv.to_csv(nombre_archivo, index=False, sep=',')
        msg.showinfo("Éxito", "El csv ha sido guardado con éxito.")

def terminar_root():
    '''Termina la ventana principal
    '''
    root.quit()
    root.destroy()

def info_programa():
    msg.showinfo('SAEM',
'''Sistema de Almacenamiento y Explotación de Metabolitos.
Software desarrollado en el marco del convenio de trabajo de la Tecnicatura Universitaria en Explotación de Datos 
(TUPED) de la FIUNER.\n 
Autor: Colazo Maximiliano G.
Contacto: maximiliano.colazo@uner.edu.ar''')    
#---------------------------------------------------------------------------------------------
# Crear la ventana de la interfaz gráfica
root = tk.Tk()
#root.geometry('300x330')
root.title('SAEM')
#creando un menu
menu_bar = Menu(root)
root.config(menu=menu_bar)
#agregando items
file = Menu(menu_bar, tearoff=0)
file.add_command(label='Cargar Base de Datos', command=cargar_archivo)
file.add_separator()
file.add_command(label='Procesar Base de Datos', command=generar_ventana_de_procesamiento)
file.add_separator()
file.add_command(label='Salir', command=terminar_root)
menu_bar.add_cascade(label='Inicio', menu=file)

ayuda = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='Ayuda', menu=ayuda)
ayuda.add_command(label='Acerca de', command=info_programa)

#root.iconbitmap('./imagenes/icon.ico')
if getattr(sys, 'frozen', False):
    # Si se está ejecutando desde un ejecutable generado por PyInstaller
    imagen_path = sys._MEIPASS + "./imagen.png"
else:
    # Si se está ejecutando desde el código fuente
    imagen_path = "./imagenes/imagen.png"

image = Image.open(imagen_path)
imagen_tk = ImageTk.PhotoImage(image)

# Crear un widget Label y mostrar la imagen
label_imagen = ttk.Label(root, image=imagen_tk)
label_imagen.grid(row=0, column= 0)

root.resizable(False, False)
# Ejecutar el bucle principal de la interfaz gráfica
root.mainloop()