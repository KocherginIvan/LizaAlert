def promt_st():
    standart = 0.35
    promt_standart = {
    'human face' : 0.35,
    'car' : 0.3,
    'dog' : 0.35,
    'body' : 0.45,
    'helicopter' : 0.5,
    'copter' : 0.35
    }
    return promt_standart, standart
def build_promt_start():
    promt_standart, _ = promt_st()    
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
    promt_standart, standart = promt_st()
    promt, promt_list, treshold = promt_build(promt_standart, promt_list_1, standart)    
    return promt, promt_list, treshold

def promter_test(promt_list_1, treshold):   
    #promt_standart, standart = promt_st()
    promt, promt_list, treshold = promt_test(promt_list_1, treshold)    
    return promt, promt_list, treshold