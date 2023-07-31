

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from declarative_base import Base

class Imagen(Base):
    '''Modela una imagen con sus atributos y funcionalidades'''
    __tablename__ = 'imagen'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    fecha = Column(String)
    paciente_id = Column(Integer, ForeignKey('paciente.id'))
    paciente = relationship('Paciente', back_populates='imagenes')
    voxeles = relationship('Voxel')

    def __init__(self, nombre, fecha, paciente):
        self.nombre = nombre
        self.fecha = fecha
        self.paciente = paciente

    def __str__(self):
        return f'{self.nombre} {self.fecha}'
