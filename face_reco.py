import numpy as np
#import os
# from PIL import Image, ImageDraw

from sqlalch import get_id_for_calname, add_vector
from sqlalchemy import create_engine, Column, Integer, String, BLOB, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.types import TypeDecorator, PickleType

import pickle
import face_recognition

СALLSIGN_ID     = {}
СALLSIGN_NAME   = {}
VECTORS         = {}

#( sqlalchemy
Base = declarative_base()

class PickleTypeDecorator(TypeDecorator):
    impl = BLOB
    cache_ok = False
    def process_bind_param(self, value, dialect):
        if value is not None:
            return pickle.dumps(value)

    def process_result_value(self, value, dialect):
        if value is not None:
            return pickle.loads(value)

class Callsign(Base):
    __tablename__ = 'callsign'

    id = Column(Integer, primary_key=True)
    callname = Column(String, unique=True, nullable=False)

class Vector(Base):
    __tablename__ = 'vectors'

    id = Column(Integer, primary_key=True)
    vector = Column(PickleTypeDecorator)
    #vector = Column(BLOB, nullable=False)
    #img = Column(BLOB, unique=True, nullable=True)
    call_id = Column(Integer, ForeignKey('callsign.id'))
    call = relationship('Callsign', back_populates='vectors')

Callsign.vectors = relationship('Vector', order_by=Vector.call_id, back_populates='call')

# Создание базы данных
Base = declarative_base()
engine = create_engine('sqlite:///la.db', echo=False)
Base.metadata.create_all(bind=engine)

class PickleTypeDecorator(TypeDecorator):
    impl = BLOB

    def process_bind_param(self, value, dialect):
        if value is not None:
            return pickle.dumps(value)

    def process_result_value(self, value, dialect):
        if value is not None:
            return pickle.loads(value)

def sess():
    # Создание сессии для работы с базой данных
    Session = sessionmaker(bind=engine)
    return Session()

def add_vector(id, callvector): #, callname

    ses = sess()

    # Добавление записей в таблицы
    #call = Callsign(callname=callname)
    vector = Vector(call_id=id, vector=callvector) #, call=call

    ses.add_all([vector]) #call, 
    ses.commit()

def get_vectors(callid) -> list:
    # Запрос к базе для получения списка значений vector с фильтром по callname
    #global СALLSIGN_ID
    ses = sess()

    vectors_for_callname = (
        ses.query(Vector.vector)
        #.join(Vector.call)
        .filter(Vector.call_id == callid)
        .all()
    ) # выводит во внутреннем формате query
    # переводим в формат numpy.array
    list_vec = []
    for i in vectors_for_callname:
        qq = i[0][0]
        list_vec.append(qq)    
    #print(f'Vectors for callname {СALLSIGN_ID[callid]}: {vectors_for_callname}')
    return list_vec

def get_id_for_calname(callname) -> int: 
    ses = sess()
    # Запрос к базе для получения получения всех позывных call_id
    result = (ses.query(Callsign.id).filter(Callsign.callname == callname).one())
    return result.id
#) sqlalchemy

#( face
class Faces_Recognition():
    img = None  # str - путь к файлу
    jit = 1
    model = "large"  # "small"  
    loc_model = 'cnn' # 'hog'- for CPU, 'cnn' - for GPU
    array_img = []
    bbox = []
    vector = []
    tolerance = 0.6
    number_of_times_to_upsample = 1
    def __init__(self, img):
        if type(img) == str:
            self.img = img
            self.array_img = self.get_array()
        elif type(img) == np.ndarray:
            self.array_img = img  

    def get_array(self): 
        self.array_img = face_recognition.load_image_file(self.img)
        return self.array_img

    def get_bbox(self): 
        self.bbox = face_recognition.face_locations(self.array_img, model=self.loc_model)
        return self.bbox

    def get_vector(self):
        self.vector = face_recognition.face_encodings(
            face_image=self.array_img, 
            known_face_locations=self.bbox, 
            num_jitters=self.jit, 
            model=self.model)
        return self.vector

    def convert_bbox(top, right, bottom, left) -> list:  
        '''
        return [x_цента, у_центра, ширина, высота]
        '''
        width = right - left
        height = bottom - top
        center_x = left + width / 2
        center_y = top + height / 2
        return [center_x,center_y,width,height]

    def _normalize_rez(self,rez) -> dict:
        keys_to_remove = []

        for key, value in rez.items():
            sublist = value[1]
            subvalue = value[2]
            
            # Проверяем, есть ли такое значение sublist в оставшихся элементах словаря
            for other_key, other_value in rez.items():
                if other_key != key:
                    if other_value[1] == sublist and other_value[2] > subvalue:
                        # Если находим такое же sublist с большим subvalue, добавляем ключ для удаления
                        keys_to_remove.append(key)
                        break
                    elif other_value[1] == sublist and other_value[2] < subvalue:
                        # Если находим такое же sublist с меньшим или равным subvalue, добавляем ключ другого элемента для удаления
                        keys_to_remove.append(other_key)
                        break

        # Удаляем все ключи, указанные для удаления
        keys_to_remove = set(keys_to_remove)
        for key in keys_to_remove:
            del rez[key]

        return rez

    def recognition(self):
        global VECTORS 
        if VECTORS == {}:
            VECTORS = get_all_vectors()

        self.bbox   = self.get_bbox()
        self.vector = self.get_vector()           
        index_to_name = {}

        for i, (top, right, bottom, left) in enumerate(self.bbox):

            # Поиск совпадений в базе векторов
            for name, known_encodings_list in VECTORS.items():
                matches_count = 0
                # for known_encoding in known_encodings_list:
                match = face_recognition.compare_faces(known_encodings_list, self.vector[i], tolerance=self.tolerance)
                #print(len(match),match)
                for m in match:
                    if m:
                        matches_count += 1
                coincidence = matches_count/len(known_encodings_list) # Коэффициент уверенности распознавания
                if coincidence > 0.2:
                    # Проверяю
                    if name in index_to_name:
                        coin = index_to_name[name][2]
                        if coin<coincidence:
                            width = right - left
                            height = bottom - top
                            center_x = int(left + width / 2)
                            center_y = int(top + height / 2)
                            bbox = [center_x,center_y,width,height]
                            bbox2= [top, right, bottom, left]
                            index_to_name[name] = [bbox, bbox2, coincidence] 
                    else:
                        width = right - left
                        height = bottom - top
                        center_x = int(left + width / 2)
                        center_y = int(top + height / 2)
                        bbox = [center_x,center_y,width,height]
                        bbox2= [top, right, bottom, left]
                        index_to_name[name] = [bbox, bbox2, coincidence]

        return self._normalize_rez(index_to_name)
#) face

#( enveronments
def get_all_calnames(): 
    """
    Retrieves all call names from the database and assigns them to global variables.
    Returns:
        None
    """
    global СALLSIGN_ID, СALLSIGN_NAME
    ses = sess()
    # Запрос к базе для получения всех позывных call_id
    
    result = (ses.query(Callsign.id, Callsign.callname).all())
    result_id       = {callname: id for id, callname in result}
    result_name     = {id:callname for id, callname in result}
    СALLSIGN_ID     = result_id
    СALLSIGN_NAME   = result_name
    #return result_id, result_name

def get_all_vectors() -> dict:
    vec = {}
    for name, id in СALLSIGN_ID.items():
        vec[name] = get_vectors(id)
    return vec

get_all_calnames()
VECTORS = get_all_vectors()  # словарь со Всеми векторами всех поисковиков    
#) enveronments
