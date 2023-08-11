

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from modulos.declarative_base import Base

class Region(Base):
    '''Modela una region del cerebro. Tiene los atributos y funcionalidades para 
    representar una region'''
    __tablename__ = 'region'

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    nombre = Column(String)
    voxeles = relationship('Voxel', back_populates='region')

    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
      
    def __str__(self):
        return f"{self.nombre}"
    
