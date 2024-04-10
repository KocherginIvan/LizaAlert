def promt_st():
    standart = 0.35
    promt_standart = {
    'car' : 0.3,
    'dog' : 0.35,
    'helicopter' : 0.6,
    'drone' : 0.45,
    'ambulance': 0.5  ,
    #'rescuer': 0.5  ,
    #'forest': 0.5  ,
    'horse': 0.5  ,
    'stretcher': 0.5  ,
    'road': 0.5  ,
    'hugs': 0.5  ,
    'tears': 0.5  ,
    #'police': 0.5  ,
    'snowmobile': 0.5  ,
    'water': 0.5  ,
    'tractor': 0.5  ,
    #'quad bike': 0.5  ,
    'truck': 0.5  ,
    'lake': 0.45
    }
    promt_rus_dict = {
    'car': 'Машина',
    'dog':  'Собака',
    'helicopter': 'Вертолет',
    'drone': 'БПЛА',
    'ambulance': 'Скорая помощь',
    #'rescuer': 'Спасатель',
    #'forest': 'Лес',
    'horse': 'Лошадь',
    'stretcher': 'Носилки',
    'road': 'Дорога',
    'hugs': 'Объятия',
    'tears': 'Слёзы',
    'police': 'Полиция',
    'snowmobile': 'Снегоход',
    'reservoir': 'Водоём',
    'army': 'Армия',
    'suspension bridge': 'Навесной мост',
    'ferry crossing': 'Паромная переправа',
    'tractor': 'Вездеход',
    'quad bike': 'Квадроцикл',
    'truck': 'Грузовик',
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