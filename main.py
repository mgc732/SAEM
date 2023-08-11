# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 10:42:10 2023

@author: Max
"""
from sqlalchemy import func
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
def guardar_bd(cabecera, matriz_region, imagen_recortada):
    """ Guarda información en una base de datos utilizando SQLAlchemy.
    Parámetros:
        cabecera (dict): Un diccionario que contiene información de la cabecera, incluyendo:
            - 'id' (int): ID del paciente.
            - 'nombre' (str): Nombre del paciente.
            - 'apellido' (str): Apellido del paciente.
            - 'edad' (int): Edad del paciente.
            - 'genero' (str): Género del paciente.
            - 'imagen' (str): Nombre de la imagen.
            - 'fecha' (str): Fecha de la imagen.
            - 'metabolito' (str): Nombre del metabolito.

        matriz_region (list): Una matriz (lista de listas) que representa la región del cerebro.
        imagen_recortada (list): Una matriz (lista de listas) que representa la imagen recortada.
    Notas:
        - La función utiliza SQLAlchemy para interactuar con la base de datos.
        - Verifica si el objeto paciente ya existe en la base de datos y lo agrega si no existe.
        - Agrega la imagen y la información del metabolito en la base de datos.
        - Actualiza el estado del widget label_base según el resultado de la operación.
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
        paciente_mem = Paciente(id=cabecera['id'], 
                            nombre=cabecera['nombre'],
                            apellido=cabecera['apellido'], 
                            edad=cabecera['edad'], 
                            genero=cabecera['genero'])
        imagen_mem = Imagen(nombre=cabecera['imagen'], fecha =cabecera['fecha'])
        paciente_bd = session.query(Paciente).filter_by(id=paciente_mem.id).first() 
        
        # Si no existe el paciente, lo agrego
        if paciente_bd is None:
            #session.add(paciente)
            #imagen = Imagen(nombre=cabecera['imagen'], fecha =cabecera['fecha'], paciente=paciente)
            #session.add(imagen)
            #paciente.imagenes.append(imagen)
            for i in range(len(matriz_region)):
                for j in range(len(matriz_region[0])):
                    if matriz_region[i][j]!=0:
                        metabolito = Metabolito(nombre=cabecera['metabolito'], concentracion= imagen_recortada[i][j])
                        #session.add(metabolito)
                        voxel = Voxel(fila=i, columna= j)
                        #session.add(voxel)
                        voxel.region = session.get(Region, int(matriz_region[i][j]))
                        voxel.metabolitos.append(metabolito)
                        #metabolito.voxel = voxel
                        imagen_mem.voxeles.append(voxel)
            paciente_mem.imagenes.append(imagen_mem)
            session.add(paciente_mem)
            #print('Registro agregado(1)')
            msg.showinfo('Base de datos','Agregado nuevo Paciente') 

        # Si existe el paciente pero no existe la imagen, la agrego
        elif imagen_mem.id not in [ima.id for ima in paciente_bd.imagenes]:
            #paciente = session.merge(paciente)
            #imagen = Imagen(nombre=cabecera['imagen'], fecha =cabecera['fecha'], paciente=paciente)
            #session.add(imagen)
            #paciente.imagenes.append(imagen)
            for i in range(len(matriz_region)):
                for j in range(len(matriz_region[0])):
                    if matriz_region[i][j]!=0:
                        metabolito = Metabolito(nombre=cabecera['metabolito'], concentracion= imagen_recortada[i][j])
                        #session.add(metabolito)
                        voxel = Voxel(fila=i, columna= j)
                        #session.add(voxel)
                        voxel.region = session.get(Region, int(matriz_region[i][j]))
                        voxel.metabolitos.append(metabolito)
                        #metabolito.voxel = voxel
                        imagen_mem.voxeles.append(voxel)
            paciente_bd.imagenes.append(imagen_mem)
            #print('Registro agregado (2)')
            msg.showinfo('Base de datos', 'Nueva imagen asociada al paciente') 

        else: 
            imagen_bd = session.query(Imagen).filter_by(id=imagen_mem.id).first()
            lista_tuplas = [(i, j) for i in range(len(matriz_region)) for j in range(len(matriz_region[0])) if matriz_region[i][j]!=0]
            #print(lista_tuplas)
            for tupla in lista_tuplas:
                voxel = Voxel(fila=tupla[0], columna= tupla[1])
                voxel.region = session.get(Region, int(matriz_region[tupla[0]][tupla[1]]))
                if voxel not in [vox_db for vox_db in imagen_bd.voxeles]:
                    metabolito = Metabolito(nombre=cabecera['metabolito'], concentracion= imagen_recortada[tupla[0]][tupla[1]])
                    voxel.metabolitos.append(metabolito)
                    imagen_bd.voxeles.append(voxel)
                    msg.showinfo('Base de datos', 'Nuevo voxel asociado a la imagen')
                else:
                    vox_bd = imagen_bd.voxeles[imagen_bd.voxeles.index(voxel)]                                                        
                    if cabecera['metabolito'] not in [meta.nombre for meta in vox_bd.metabolitos] and vox_bd.region_id == int(matriz_region[tupla[0]][tupla[1]]):
                        #print(vox_bd.region_id, int(matriz_region[tupla[0]][tupla[1]]))
                        metabolito = Metabolito(nombre=cabecera['metabolito'],  concentracion= imagen_recortada[tupla[0]][tupla[1]])
                        vox_bd.metabolitos.append(metabolito)
                        msg.showinfo('Base de datos', 'Nuevo Metabolito asociado')
                    else:
                        msg.showwarning('Base de datos', 'Compruebe los datos')

      
        session.commit()
        session.close()
    else:
        if np.all(matriz_region == 0):
            msg.showerror('Base de datos', 'Regiones vacía') 
        else:
            msg.showerror('Base de datos', 'Restricción de edad\nEl paciente es menor de edad')  

def guardar_region(filas, columnas, cabecera, imagen_recortada):
    """ Guarda información en una matriz de regiones y llama a la función 'guardar_bd' para guardarla en una base de datos.
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
        - Llama a la función 'guardar_bd' para guardar la información en una base de datos.
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
    guardar_bd(cabecera, matriz_region, imagen_recortada)

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
    norm_valor = (valor - vmin) / (vmax - vmin)
    cmap = plt.get_cmap(colormap)
    rgba = cmap(norm_valor)
    #rgba = get_rgba(norm_valor)
    r = int(rgba[0] * 255)
    g = int(rgba[1] * 255)
    b = int(rgba[2] * 255)
    return f'#{r:02x}{g:02x}{b:02x}'

def crear_ventana_matriz(filas, columnas, cabecera, imagen_recortada):
    """ Crea una ventana emergente para ingresar las regiones de la matriz.
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
        - Al hacer clic en el botón 'Guardar', llama a la función 'guardar_region' para guardar la información 
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
    
    btn_guardar = ttk.Button(ventana_matriz, text="Guardar", command=lambda: guardar_region(filas, columnas, cabecera, imagen_recortada))
    btn_guardar.grid(row=filas*2+2, columnspan=columnas, pady=10)
    ventana_matriz.resizable(False, False)
  
def ventana_figura(image):
    """ Crea una ventana emergente que muestra una imagen utilizando Matplotlib y Tkinter.
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
    pos = ax1.imshow(image)
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
        - Muestra la imagen en una ventana emergente utilizando la función 'ventana_figura'.
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
        if 'PixelData' in dataset:
            image = dataset.pixel_array

            if not np.all(image == 0):
                # Recortar la matriz utilizando los índices     
                filas_no_cero, columnas_no_cero = np.nonzero(image)
                image_recortada = image[min(filas_no_cero):max(filas_no_cero)+1, min(columnas_no_cero):max(columnas_no_cero)+1]
                filas = np.shape(image_recortada)[0]
                columnas = np.shape(image_recortada)[1]

                # Actualizar el label con el mensaje de carga exitosa del archivo
                msg.showinfo('Lectura exitosa del archivo DICOM', cabecera_inf)
                crear_ventana_matriz(filas, columnas, cabecera, image_recortada)
                ventana_figura(image_recortada)
                
            else:
                # Actualizar el label con el mensaje de carga exitosa del archivo
                msg.showinfo('Lectura exitosa del archivo DICOM', '      No hay datos asociados a una imagen      ')

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
        tk.Label(frame_region, text=f" Relación de Naa/Cre ==> {ratios['N-Acetyl/Creatine'].mean():.3f} ",
                 font=f'Helvetica {letra} bold').grid(row=2, column=2, sticky='W')
        tk.Label(frame_region, text=f" Relación de Cho/Cre ==> {ratios['Choline/Creatine'].mean():.3f} ",
                 font=f'Helvetica {letra} bold').grid(row=3, column=2, sticky='W')
        tk.Label(frame_region, text=f" Creatine + Choline    ==> {(ratios['Creatine']+ratios['Choline']).mean():.1f} ",
                 font=f'Helvetica {letra} bold').grid(row=4, column=2, sticky='W')
        tk.Label(frame_region, text=f" Relación de Cho/Naa ==> {ratios['Choline/N-Acetyl'].mean():.3f} ",
                 font=f'Helvetica {letra} bold').grid(row=5, column=2, sticky='W')
        tk.Label(frame_region, text=f" Relación de Naa/Cho ==> {ratios['N-Acetyl/Choline'].mean():.3f} ",
                 font=f'Helvetica {letra} bold').grid(row=6, column=2, sticky='W')
        tk.Label(frame_region, text=f" Relación de Cre/Naa  ==> {ratios['Creatine/N-Acetyl'].mean():.3f} ",
                 font=f'Helvetica {letra} bold').grid(row=7, column=2, sticky='W')
        
    else:
        # Si el DataFrame está vacío, mostrar un mensaje de advertencia
        msg.showwarning("Advertencia", "No hay elementos para guardar.")

def mostrar_metabolitos():
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
            * Relación de Cre/Naa'''
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
    if df.empty:
            msg.showwarning("Advertencia", "No hay elementos para guardar.")
    else:
        nombre_region = df['region'].iloc[0]
        nombre_archivo = f'./data/datos_metabolitos_{nombre_region}.csv'

        df_csv = df.drop(columns=['nombre_metabolito', 'concentracion'])
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
        '''
        correlation_with_age = df.drop(columns=['id_paciente',
                                            'nombre_metabolito',
                                            'concentracion',
                                            'region', 
                                            'fecha_imagen',
                                            'Choline',
                                            'N-Acetyl',
                                            'Creatine',
                                            'genero']).corr()['edad'].drop('edad')
        print(correlation_with_age)'''
        df_csv.to_csv(nombre_archivo, index=False, sep=',')
        msg.showinfo("Éxito", "El csv ha sido guardado con éxito.")

def terminar_root():
    '''Termina la ventana principal
    '''
    root.quit()
    root.destroy()

def info_programa():
    msg.showinfo('SPEAM',
'''Sistema de Procesamiento, Explotación y Almacenamiento de Metabolitos.
Software desarrollado en el marco del convenio de trabajo de la Tecnicatura Universitaria en Explotación de Datos 
(TUPED) de la FIUNER.\n 
Autor: Colazo Maximiliano G.
Contacto: maximiliano.colazo@uner.edu.ar''')    
#---------------------------------------------------------------------------------------------
# Crear la ventana de la interfaz gráfica
root = tk.Tk()
#root.geometry('300x330')
root.title('SPEAM')
#creando un menu
menu_bar = Menu(root)
root.config(menu=menu_bar)
#agregando items
file = Menu(menu_bar, tearoff=0)
file.add_command(label='Cargar Base de Datos', command=cargar_archivo)
file.add_separator()
file.add_command(label='Procesar Base de Datos', command=mostrar_metabolitos)
file.add_separator()
file.add_command(label='Salir', command=terminar_root)
menu_bar.add_cascade(label='Inicio', menu=file)

ayuda = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='Ayuda', menu=ayuda)
ayuda.add_command(label='Acerca de', command=info_programa)

root.iconbitmap('./imagenes/icon.ico')
if getattr(sys, 'frozen', False):
    # Si se está ejecutando desde un ejecutable generado por PyInstaller
    imagen_path = sys._MEIPASS + "./imagenes/imagen.png"
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