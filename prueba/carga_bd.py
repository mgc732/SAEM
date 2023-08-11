
from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

engine = create_engine('sqlite:///prueba//prueba.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

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
        
        self.id = f'{nombre}_{fecha[:2]+fecha[3:5]+fecha[6:]}'
        self.nombre = nombre
        self.fecha = fecha
        #self.paciente = paciente

    def __str__(self):
        return f'{self.nombre} {self.fecha}'

class Voxel(Base):
    __tablename__ = 'voxel'

    id = Column(Integer, primary_key=True)
    fila = Column(Integer)
    columna = Column(Integer)
    
    metabolitos = relationship('Metabolito', back_populates='voxel')
    imagen_id = Column(Integer, ForeignKey('imagen.id'))
    imagen = relationship('Imagen', back_populates='voxeles')
    region_id = Column(Integer, ForeignKey('region.id'))
    region = relationship('Region', back_populates='voxeles')
    def __init__(self, fila, columna):
        self.fila = fila
        self.columna = columna
        #self.imagen = imagen
        
    def __str__(self):
        return f'voxel: ({self.fila}, {self.columna})'

class Metabolito(Base):
    
    __tablename__ = 'metabolito'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    concentracion = Column(Float)
    voxel_id = Column(Integer, ForeignKey('voxel.id'))
    voxel = relationship('Voxel', back_populates='metabolitos')
    
    def __init__(self, nombre, concentracion):
        self.nombre = nombre
        self.concentracion = concentracion
        #self.imagen = imagen
        
    def __str__(self):
        return f'voxel: ({self.nombre}, {self.concentracion})'

class Region(Base):
    '''Modela una region del cerebro. Tiene los atributos y funcionalidades para 
    representar una region'''
    __tablename__ = 'region'

    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    voxeles = relationship('Voxel', back_populates='region')

    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
      
    def __str__(self):
        return f"{self.nombre}"



if __name__  == '__main__':

    Base.metadata.create_all(engine)
    #Abre la sesión
    session = Session()
    
    regiones = [Region(1, 'parietal'), Region(2, 'frontal')]
    
    for region in regiones:
        if session.query(Region).filter_by(id=region.id).first() is None:
            #region1 = Region(id=1, nombre='parietal')
            session.add(region)
        else:
            print('El id ya existe en la tabla.')    
    
    
    paciente = Paciente(id='1', 
                            nombre='Max',
                            apellido='Max', 
                            edad=38, 
                            genero='M')

    if session.query(Paciente).filter_by(id=paciente.id).first() is None:
        pass    
        
        imagen0 = Imagen(nombre='IM0', fecha ='04/08/2023')
        vox0 = Voxel(0,0)
        vox0.region = regiones[1]
        vox1 = Voxel(0,1)
        vox1.region = regiones[1]
        m0 = Metabolito('naa', 123)
       # m1 = Metabolito('cre', 123)
       # m2 = Metabolito('cho', 123)
        vox0.metabolitos.append(m0)
        vox1.metabolitos.append(m0)
        #vox0.metabolitos.append(m1)
        #vox0.metabolitos.append(m2)
        imagen0.voxeles.append(vox0)
        imagen0.voxeles.append(vox1)
        #imagen1= Imagen(nombre='IM1', fecha ='04/08/2023')
        paciente.imagenes.append(imagen0)
        #paciente.imagenes.append(imagen1)
        session.add(paciente)
        
    else:
        paciente = session.query(Paciente).filter_by(id=paciente.id).first()           
        imagen0 = Imagen(nombre='IM0', fecha ='04/08/2023')
        if imagen0 not in paciente.imagenes:
            print(imagen0.id, paciente.imagenes[0].id)
            print('no esta')
            '''
            vox0 = Voxel(0,0)
            vox0.region = session.get(Region, 1)
            vox1 = Voxel(0,1)
            vox1.region = session.get(Region, 1)
            lista = [vox0, vox1]
            m0 = Metabolito('naa', 123)
            #m1 = Metabolito('cre', 123)
            #m2 = Metabolito('cho', 123)
            for vox in lista:
                vox.metabolitos.append(m0)
                imagen0.voxeles.append(vox)
           
            #imagen1= Imagen(nombre='IM1', fecha ='04/08/2023')
            paciente.imagenes.append(imagen0)
            #paciente.imagenes.append(imagen1)
        '''
        else:
            print('esta')
            '''
            imagen0 = session.query(Imagen).filter_by(id=imagen0.id).first()
            
            vox0 = Voxel(0,2)
            vox0.region = session.get(Region, 1)
            vox1 = Voxel(2,1)
            vox1.region = session.get(Region, 1)
            lista = [vox0, vox1]
            m0 = Metabolito('naa', 123)
            #m1 = Metabolito('cre', 123)
            #m2 = Metabolito('cho', 123)
            for vox in lista:
                if vox in imagen0.voxeles:
                    print('existe')
                vox.metabolitos.append(m0)
                imagen0.voxeles.append(vox)

            
            
            vox0 = Voxel(0,0)
            vox0.region = regiones[1]
            vox1 = Voxel(0,1)
            vox1.region = regiones[1]
            lista = [vox0, vox1]
            m0 = Metabolito('naa', 123)
            for vox in lista:
                vox.metabolitos.append(m0)
                if m0 not in session:
                    imagen0.voxeles.append(vox)
    '''
    session.commit()  
    session.close()


'''

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
        if paciente not in session:
            session.add(paciente)
            imagen = Imagen(nombre=cabecera['imagen'], fecha =cabecera['fecha'])
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
            msg.showinfo('Base de datos','Nuevo Paciente') 

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
            msg.showinfo('Base de datos', 'Nueva imagen asociada') 

        else: 
                #print('Registro Existente')
                msg.showinfo('Base de datos', 'Registro Existente')      

        session.close()
    else:
        if np.all(matriz_region == 0):
            msg.showerror('Base de datos', 'Matriz de regiones vacía') 

        else:
            msg.showerror('Base de datos', 'Restricción de edad\nEl paciente es menor de edad')  

'''