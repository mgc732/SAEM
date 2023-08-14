# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 10:23:11 2023

"""

from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from modulos.declarative_base import Base

class Metabolito(Base):
    """
    Clase para representar un Metabolito en la base de datos.

    Esta clase define la estructura de un Metabolito en la base de datos, que contiene información
    sobre su nombre y concentración, así como su asociación con un Voxel.

    Args:
        Base (sqlalchemy.ext.declarative.api.Base): Clase base de SQLAlchemy.

    Attributes:
        __tablename__ (str): Nombre de la tabla en la base de datos.
        id (sqlalchemy.sql.schema.Column): Columna que representa el identificador único del Metabolito.
        nombre (sqlalchemy.sql.schema.Column): Columna que almacena el nombre del Metabolito.
        concentracion (sqlalchemy.sql.schema.Column): Columna que almacena la concentración del Metabolito.
        voxel_id (sqlalchemy.sql.schema.Column): Columna que almacena el identificador del Voxel asociado.
        voxel (sqlalchemy.orm.relationship): Relación con el Voxel asociado al Metabolito.

    Methods:
        __init__(self, nombre, concentracion): Constructor de la clase Metabolito.
        __str__(self): Retorna una representación en cadena del Metabolito.

    Example:
        metabolito = Metabolito(nombre='glucosa', concentracion=5.2)
        print(metabolito)  # Imprime: "metabolito: (glucosa, 5.2)"

    """
    __tablename__ = 'metabolito'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    concentracion = Column(Float, nullable=False)
    voxel_id = Column(Integer, ForeignKey('voxel.id'))
    voxel = relationship('Voxel', back_populates='metabolitos')
   
    def __init__(self, nombre, concentracion):
        self.nombre = nombre
        self.concentracion = concentracion
        #self.imagen = imagen
       
    def __str__(self):
        return f'voxel: ({self.nombre}, {self.concentracion})'