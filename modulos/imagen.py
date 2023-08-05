

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from modulos.declarative_base import Base

class Imagen(Base):
    '''Modela una imagen con sus atributos y funcionalidades'''
    __tablename__ = 'imagen'
    id = Column(String, primary_key=True)
    nombre = Column(String)
    fecha = Column(String)
    # relacion bidireccional entre paciente e imagenes
    paciente_id = Column(Integer, ForeignKey('paciente.id'))
    paciente = relationship('Paciente', back_populates='imagenes')
    voxeles = relationship('Voxel', back_populates='imagen')
    
    def __init__(self, nombre, fecha):
       
        self.id = f'{nombre}_{fecha[:5]+fecha[6:7]+fecha[8:]}'
        self.nombre = nombre
        self.fecha = fecha
        #self.paciente = paciente


    def __str__(self):
        return f'{self.nombre} {self.fecha}'
