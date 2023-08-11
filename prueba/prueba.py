
from modulos.declarative_base import Session, engine, Base
from sqlalchemy import Integer, String, Float, func
from region import Region
from imagen import Imagen
from paciente import Paciente
from voxel import Voxel
from metabolito import Metabolito
# Configuración de la base de datos
engine = create_engine('sqlite:////Users/maximiliano.colazo/Desktop/db_dicom.db', echo=True)
session = Session(engine)

# Realizar la consulta
results = session.query(Metabolito.nombre, func.round(func.avg(Metabolito.concentracion), 2).label('promedio_concentracion'))\
                .join(Voxel, Metabolito.voxel_id == Voxel.id)\
                .join(Region, Voxel.region_id == Region.id)\
                .filter(Region.nombre == 'frontal')\
                .group_by(Metabolito.nombre)\
                .all()

# Imprimir los resultados
for nombre, promedio_concentracion in results:
    print(f"Metabolito: {nombre}, Promedio Concentración: {promedio_concentracion}")






