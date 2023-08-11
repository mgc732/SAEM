from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from modulos.declarative_base import Base

class Paciente(Base):
    '''Modela a una paciente con sus atributos y funcionalidades'''
    __tablename__ = 'paciente'
    id = Column(String, primary_key=True)
    nombre = Column(String)
    apellido = Column(String)
    edad = Column(Integer)
    genero = Column(String)
    imagenes = relationship('Imagen', back_populates='paciente')

    def __init__(self, id, nombre, apellido, edad, genero):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.edad = edad
        self.genero = genero

    def __str__(self):
        return f'\n\t{self.apellido}, {self.nombre}'


    
