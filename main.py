# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 10:42:10 2023

@author: Max
"""

from declarative_base import Session, engine, Base
from region import Region
from imagen import Imagen
from paciente import Paciente
from voxel import Voxel
from metabolito import Metabolito

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import pydicom
import numpy as np

import re
import sys



filas = 0
columnas = 0
ventana_matriz = None

#--------------------------------------------------------------
def guardar_bd(cabecera, matriz_region, imagen_recortada):
    
    matriz_region = np.array(matriz_region)
  
    
    if np.any(matriz_region != 0):
        #Crea la BD
        Base.metadata.create_all(engine)
        #Abre la sesión
        session = Session()
        #Regiones 
        regiones = []
        regiones.append(Region(id=1, nombre='pariental'))
        regiones.append(Region(id=2, nombre='frontal'))
        regiones.append(Region(id=3, nombre='occipital'))
        regiones.append(Region(id=4, nombre='temporal'))
        regiones.append(Region(id=5, nombre='nucleo'))
        
        for region in regiones:
            existing_objeto = session.get(Region, region.id)
            
            # Verificar si el objeto existe en la base de datos
            if existing_objeto:
                # El objeto ya existe en la base de datos, no es necesario volver a escribirlo
                print("El objeto ya existe en la base de datos")
            else:
                # El objeto no existe en la base de datos, puedes escribirlo
                session.add(region)
                session.commit()
                print("El objeto ha sido guardado en la base de datos")

        paciente = Paciente(id=cabecera['id'], 
                            nombre=cabecera['nombre'],
                            apellido=cabecera['apellido'], 
                            edad=cabecera['edad'], 
                            genero=cabecera['genero'])
        # Si no existe el paciente, lo agrego
        if not session.get(Paciente, paciente.id):
            session.add(paciente)
            imagen = Imagen(nombre=cabecera['imagen'], fecha =cabecera['fecha'], paciente=paciente)
            session.add(imagen)
            paciente.imagenes.append(imagen)
            
            for i in range(len(matriz_region)):
                for j in range(len(matriz_region[0])):
                    if matriz_region[i][j]!=0:
                        metabolito = Metabolito(nombre=cabecera['metabolito'], concentracion= imagen_recortada[i][j])
                        session.add(metabolito)
                        voxel = Voxel(fila=i, columna= j, imagen=imagen)
                        session.add(voxel)
                        
                        voxel.region =  session.get(Region, int(matriz_region[i][j]))
                        metabolito.voxel = voxel
                        imagen.voxeles.append(voxel)
            session.commit()
            #print('Registro agregado(1)')
            label_base.config(text="Registro agregado(1)")
            label_base.configure(foreground='green')
        # Si existe el paciente pero no existe la imagen, la agrego
        elif not session.query(Imagen).filter(Imagen.fecha==cabecera['fecha'], Imagen.paciente_id==paciente.id, Imagen.nombre==cabecera['imagen']).all():
            paciente = session.merge(paciente)
            imagen = Imagen(nombre=cabecera['imagen'], fecha =cabecera['fecha'], paciente=paciente)
            session.add(imagen)
            paciente.imagenes.append(imagen)
            
            for i in range(len(matriz_region)):
                for j in range(len(matriz_region[0])):
                    if matriz_region[i][j]!=0:
                        metabolito = Metabolito(nombre=cabecera['metabolito'], concentracion= imagen_recortada[i][j])
                        session.add(metabolito)
                        voxel = Voxel(fila=i, columna= j, imagen=imagen)
                        session.add(voxel)
                       
                        voxel.region =  session.get(Region, int(matriz_region[i][j]))
                        metabolito.voxel = voxel
                        imagen.voxeles.append(voxel)
            session.commit()
            #print('Registro agregado (2)')
            label_base.config(text="Registro agregado(2)")
            label_base.configure(foreground='green')
        else: 
                #print('Registro Existente')     
                label_base.config(text="Registro Existente")
                label_base.configure(foreground='red')
        session.close()
    else:
        label_base.config(text="Cargar matriz regiones")
        label_base.configure(foreground='red')
       

    
def guardar_texto(filas, columnas, cabecera, imagen_recortada):
    
    matriz_region = [[0]*columnas for i in range(filas)]
    
    for i in range(filas):
        for j in range(columnas):
            if not matriz_entries[i][j].get()=='':
                if matriz_entries[i][j].get() == 'Parietal':
                    matriz_region[i][j] = 1
                elif matriz_entries[i][j].get() == 'Frontal':
                    matriz_region[i][j] = 2
                elif matriz_entries[i][j].get() == 'Occipital':
                    matriz_region[i][j] = 3
                elif matriz_entries[i][j].get() == 'Temporal':
                    matriz_region[i][j] = 4
                else:
                    matriz_region[i][j] = 5
            
    ventana_matriz.destroy()  # Cerrar la ventana de la matriz al guardar
    ventana_fig.destroy()
    guardar_bd(cabecera, matriz_region, imagen_recortada)

def crear_ventana_matriz(filas, columnas, cabecera, imagen_recortada):
    global ventana_matriz
    global matriz_entries
    ventana_matriz = tk.Toplevel(root)
    ventana_matriz.title("Ingresar Regiones")
    matriz_entries = []
    opciones = ['','Parietal', 'Frontal', 'Occipital', 'Temporal', 'Nucleo']  # Lista de opciones para el Combobox
    for i in range(filas):
        fila_entries = []
        for j in range(columnas):
            
            # Crear el Combobox en la primera celda
            combo = ttk.Combobox(ventana_matriz, values=opciones)
            combo.current(0)  # Seleccionar la primera opción por defecto
            combo.grid(row=i, column=j)
            fila_entries.append(combo)

        matriz_entries.append(fila_entries)
    btn_guardar = tk.Button(ventana_matriz, text="Guardar", command=lambda: guardar_texto(filas, columnas, cabecera, imagen_recortada))
    btn_guardar.grid(row=filas, columnspan=columnas)

    
def ventana_figura(image):
   
    global ventana_fig
    ventana_fig = tk.Toplevel(root)
    ventana_fig.title("Imagen")
    # Mostrar la imagen recortada en la ventana de la matriz
    fig = plt.figure(figsize=(4, 4))
    plt.imshow(image, cmap=plt.cm.gray)
    plt.axis('off')
    plt.title('Imagen DICOM recortada')
    canvas = FigureCanvasTkAgg(fig, master=ventana_fig)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    ventana_fig.resizable(False, False)
#-------------------------------------------------------------------------------------------
def load_file():
    # Reiniciar el label a un estado en blanco
    label_carga_exitosa.config(text="")
    label_base.config(text="")
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
            'edad': re.sub('^0+', '', re.sub('[^\d]', '', dataset.PatientAge)),
            'fecha': fecha,
            'metabolito': metabolito,
            'imagen' :  re.search(r"DICOM/PA\d/.+/IM\d", file_path).group()
        }    

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
                label_carga_exitosa.config(text="Carga exitosa del archivo")
                label_carga_exitosa.configure(foreground='green')
                # Crear la ventana de la matriz para ingresar texto
                crear_ventana_matriz(filas, columnas, cabecera, image_recortada)
                ventana_figura(image_recortada)
                
            else:
                # Actualizar el label con el mensaje de carga exitosa del archivo
                label_carga_exitosa.config(text="Carga exitosa\n No hay datos de imagen")
                label_carga_exitosa.configure(foreground='red')

def terminar_bucle():
    '''Termina la ventana principal
    '''
    root.quit()
# Crear la ventana de la interfaz gráfica
root = tk.Tk()
root.geometry('300x330')
root.title('SPEAM')
#root.iconbitmap('./icon.ico')
# Crear el botón para cargar el archivo
button = tk.Button(root, text="Cargar archivo", command=load_file)
button.place(x=50, y=250)
# Agregar botón de terminar
btn_terminar = tk.Button(root, text="Terminar", command=terminar_bucle)
btn_terminar.place(x=200, y=250)

if getattr(sys, 'frozen', False):
    # Si se está ejecutando desde un ejecutable generado por PyInstaller
    imagen_path = sys._MEIPASS + "./imagen.png"
else:
    # Si se está ejecutando desde el código fuente
    imagen_path = "./imagen.png"

image = Image.open(imagen_path)
imagen_tk = ImageTk.PhotoImage(image)

# Crear un widget Label y mostrar la imagen
label_imagen = tk.Label(root, image=imagen_tk)
label_imagen.place(x=37.5, y=10)

# Crear el label para mostrar el mensaje de carga exitosa del archivo
label_carga_exitosa = tk.Label(root, text="")
label_carga_exitosa.place(x=50, y=280)
label_base = tk.Label(root, text="")
label_base.place(x=50, y=300)

root.resizable(False, False)
# Ejecutar el bucle principal de la interfaz gráfica
root.mainloop()
