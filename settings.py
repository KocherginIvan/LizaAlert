def promt_st():
    standart = 0.35
    promt_standart = {
    'human face' : 0.35,
    'car' : 0.3,
    'dog' : 0.35,
    'helicopter' : 0.5,
    'copter' : 0.35,
    'evacuation on hand': 0.35 ,
    'ambulance': 0.5  ,
    'rescuer': 0.5  ,
    'kitchen': 0.5  ,
    'children': 0.5  ,
    'forest': 0.5  ,
    'horse': 0.5  ,
    'human': 0.5  ,
    'crossing': 0.5  ,
    'stretcher': 0.5  ,
    'road': 0.5  ,
    'swamp': 0.5  ,
    'hugs': 0.5  ,
    'tears': 0.5  ,
    'police': 0.5  ,
    'pond': 0.5  ,
    'owl': 0.5  ,
    'hospital': 0.5  ,
    'cat': 0.5  ,
    'snowmobile': 0.5  ,
    'diver': 0.3  ,
    'bicycle': 0.5  ,
    'army': 0.5  ,
    'suspension bridge': 0.5  ,
    'ferry crossing': 0.5  ,
    'tractor': 0.5  ,
    'quad bike': 0.5  ,
    'transmitter': 0.5  ,
    'Railway station': 0.5  
    }
    promt_rus_dict = {
    'human face': 'Лицо человека',
    'car': 'Машина',
    'dog':  'Собака',
    'helicopter': 'Вертолет',
    'copter': 'БПЛА',
    'evacuation on hand': 'эвакуация на руках',
    'ambulance': 'Скорая помощь',
    'rescuer': 'Спасатель',
    'kitchen': 'Кухня',
    'children': 'Ребенок',
    'forest': 'Лес',
    'horse': 'Лошадь',
    'human': 'Человек',
    'crossing': 'Переправа',
    'stretcher': 'Носилки',
    'road': 'Дорога',
    'swamp': 'Болото',
    'hugs': 'Объятия',
    'tears': 'Слёзы',
    'police': 'Полиция',
    'pond': 'Пруд',
    'owl': 'Сова',
    'hospital': 'Больница',
    'cat': 'Кот',
    'snowmobile': 'Снегоход',
    'diver': 'Водолаз',
    'bicycle': 'Велосипед',
    'army': 'Армия',
    'suspension bridge': 'Навесной мост',
    'ferry crossing': 'Паромная переправа',
    'tractor': 'Трактор',
    'quad bike': 'Квадроцикл',
    'transmitter': 'Рация',
    'Railway station': 'Вокзал'
    }
    return promt_standart, standart, promt_rus_dict
def build_promt_start():
    promt_standart, _, _ = promt_st()    
    pt_st = []
    for i in promt_standart:
        pt_st.append(i)
    promt_start = pt_st[0]
    for i in range(1, len(pt_st)):
        promt_start += ' . ' + pt_st[i]
    return promt_start
def promt_build(promt_standart, promt_list_1, standart):
    promt_list = []
    treshold = []
    try:
        for j in promt_list_1:
            if j in promt_standart:
                promt_list.append(j)
                treshold.append(promt_standart[j])
            else:
                promt_list.append(j)
                treshold.append(standart)
    except: 
        print('')
    for i in promt_standart:
        if i in promt_list:
            a = 0
        else:
            promt_list.append(i) 
            treshold.append(promt_standart[i])         
    promt = promt_list[0]
    for i in range(1,len(promt_list)):        
        promt = promt + ' . ' + promt_list[i]
    return promt, promt_list, treshold

def promt_test(promt_list_1, treshold_1):
    treshold = []
    promt_list = []
    try:
        for j in promt_list_1:
            promt_list.append(j)
            treshold.append(treshold_1)
    except: 
        print('')
    promt = promt_list[0]
    for i in range(1,len(promt_list)):        
        promt = promt + ' . ' + promt_list[i]
    return promt, promt_list, treshold    

def promter(promt_list_1):   
    promt_standart, standart, _ = promt_st()
    promt, promt_list, treshold = promt_build(promt_standart, promt_list_1, standart)    
    return promt, promt_list, treshold

def promter_test(promt_list_1, treshold):   
    #promt_standart, standart = promt_st()
    promt, promt_list, treshold = promt_test(promt_list_1, treshold)    
    return promt, promt_list, treshold
def promt_to_rus(promt_list):
    _, _, promt_rus_dict = promt_st()
    promt_list_rus = []
    for i in promt_list:
        if i in promt_rus_dict:
            promt_list_rus.append(promt_rus_dict[i])
        else:
            promt_list_rus.append(i)
    return promt_list_rus