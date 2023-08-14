# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 10:33:29 2023

"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from modulos.declarative_base import Base

class Voxel(Base):
    """
    Clase para representar un Voxel en la base de datos.

    Esta clase define la estructura de un Voxel en la base de datos, que contiene información
    sobre su posición en una imagen, así como su asociación con Metabolitos, Imagen y Región.

    Args:
        Base (sqlalchemy.ext.declarative.api.Base): Clase base de SQLAlchemy.

    Attributes:
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id (sqlalchemy.sql.schema.Column): Columna que representa el identificador único del Voxel.
        fila (sqlalchemy.sql.schema.Column): Columna que almacena la fila del Voxel en la imagen.
        columna (sqlalchemy.sql.schema.Column): Columna que almacena la columna del Voxel en la imagen.
        metabolitos (sqlalchemy.orm.relationship): Relación con objetos Metabolito asociados.
        imagen_id (sqlalchemy.sql.schema.Column): Columna que almacena el identificador de la Imagen asociada.
        imagen (sqlalchemy.orm.relationship): Relación con la Imagen asociada al Voxel.
        region_id (sqlalchemy.sql.schema.Column): Columna que almacena el identificador de la Región asociada.
        region (sqlalchemy.orm.relationship): Relación con la Región asociada al Voxel.

    Methods:
        __init__(self, fila, columna): Constructor de la clase Voxel.
        __str__(self): Retorna una representación en cadena del Voxel.
        __eq__(self, objeto): Compara si dos Voxel son iguales en términos de fila y columna.

    Example:
        voxel = Voxel(fila=2, columna=3)
        print(voxel)  # Imprime: "voxel: (2, 3)"
        if voxel1 == voxel2:
            print("Los Voxel son iguales")

    """
    __tablename__ = 'voxel'
    id = Column(Integer, primary_key=True)
    fila = Column(Integer, nullable=False)
    columna = Column(Integer, nullable=False)
   
    metabolitos = relationship('Metabolito', back_populates='voxel')
    imagen_id = Column(Integer, ForeignKey('imagen.id'))
    imagen = relationship('Imagen', back_populates='voxeles')
    region_id = Column(Integer, ForeignKey('region.id'))
    region = relationship('Region', back_populates='voxeles')
    
    def __init__(self, fila, columna):
        #self.id = f'{fila}_{columna}_{idimagen}'
        self.fila = fila
        self.columna = columna
        #self.imagen = imagen
    def __str__(self):
        return f'voxel: ({self.fila}, {self.columna})'
    
    def __eq__(self, objeto):
        return self.fila == objeto.fila and self.columna == objeto.columna 
  
   
   