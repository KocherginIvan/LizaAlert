def promt_st():
    standart = 0.35
    promt_standart = {
    'car' : 0.3,
    'dog' : 0.35,
    'helicopter' : 0.6,
    'drone' : 0.45,
    'ambulance': 0.4  ,
    #'rescuer': 0.5  ,
    #'forest': 0.5  ,
    'horse': 0.4  ,
    'stretcher': 0.4  ,
    'road': 0.4  ,
    'hugs': 0.4  ,
    #'tears': 0.5  ,
    #'police': 0.5  ,
    'snowmobile': 0.4  ,
    'water': 0.4  ,
    'tractor': 0.4  ,
    #'quad bike': 0.5  ,
    'truck': 0.4  ,
    #'lake': 0.4
    }
    promt_rus_dict = {
    'car': 'Транспортное средство',
    'dog':  'Собака',
    'helicopter': 'БПЛА/Вертолет',
    'drone': 'БПЛА/Вертолет',
    'ambulance': 'Транспортное средство',
    #'rescuer': 'Спасатель',
    #'forest': 'Лес',
    'horse': 'Лошадь',
    'stretcher': 'Носилки',
    'road': 'Дорога',
    'hugs': 'Объятия',
    #'tears': 'Слёзы',
    'police': 'Полиция',
    'snowmobile': 'Транспортное средство',
    'reservoir': 'Водоём',
    'army': 'Армия',
    'suspension bridge': 'Навесной мост',
    'ferry crossing': 'Паромная переправа',
    'tractor': 'Транспортное средство',
    'quad bike': 'Транспортное средство',
    'truck': 'Транспортное средство',
    'lake': 'Водоём',
    'water': 'Водоём'
    }
    #color_standart = {'Машина' : 
    #    }
    
    return promt_standart, standart, promt_rus_dict
def build_promt_start():
    promt_standart, _, _ = promt_st()    
    pt_st = []
    th_st = []
    for i in promt_standart:
        pt_st.append(i)
        th_st.append(promt_standart[i])
    promt_start = pt_st[0]
    for i in range(1, len(pt_st)):
        promt_start += ' . ' + pt_st[i]

          
    return promt_start
def color_seach():
    search_list = [
        'Ватсон',
        'Будагов',
        'СнежныйБарс',
        'Василий',
        'Воркута',
        'Веснушка',
        'ВК74',
        'Мохнатый',
        'Евген',
        'Незабудка',
        'Лентяй',
        'Якимчинк',
        'Крапива',
        'Ёж',
        'Пифа',
        'ГБ',
        'Семён',
        'Дулин',
        'Весна',
        'Кеслер',
        'Физрук',
        'Клёцин',
        'Нибилунг',
        'МиСи',
        'Чайка'
        ]
    season_list = ['Холодный сезон',
                   'Теплый сезон',
                    'В городе',
                     'Загород/Парк', 'Светлое время суток', 'Темное время суток']
    return search_list, season_list

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