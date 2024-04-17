from LizaAlert.face_reco import Faces_Recognition
import matplotlib.pyplot as plt
import face_recognition


def main(img_path):

    faces = Faces_Recognition(img_path)
    ''' 
    faces.jit - Сколько раз повторять выборку лица при расчете кодировки. 
    Чем выше, тем точнее, но медленнее (т. е. 100 — в 100 раз медленнее)
    '''
    faces.jit = 1  

    # 'hog'- CPU, 'cnn'- GPU 
    faces.loc_model = 'hog' 

    '''
    Какое расстояние между лицами, чтобы считать его совпадающим. 
    Нижний более строгий. 
    Float - 0,6 — типичная лучшая производительность.
    '''
    faces.tolerance = 0.6

    '''
    param: number_of_times_to_upsample: сколько раз повышать дискретизацию изображения в поисках лиц. 
    Чем выше число, тем меньше лица.
    '''
    faces.number_of_times_to_upsample = 1

    rez = faces.recognition()
    print(rez)
    return rez

if __name__ == '__main__':
    img_path = 'img/in/01_ГБ/dsc09569.jpg'
    reco = main(img_path)
    for key, value in reco.items():
        print(key, value, sep='\t\t\t ')
    
    image = face_recognition.load_image_file(img_path)
    height, width = image.shape[:2]
    plt.figure(figsize=(width/50, height/50))

    plt.imshow(image, extent=[0, width, height, 0])
    plt.axis('off')

    for name, bbox in reco.items():
        top, right, bottom, left = bbox[1]
        # Отрисовка рамок вокруг найденных лиц
        plt.plot([left, right, right, left, left], [top, top, bottom, bottom, top], color='red')
        plt.text(left, top, f'{name}-{round(bbox[2]*100,2)}%', fontsize=5, bbox=dict(facecolor='GreenYellow', alpha=0.3))

    plt.show()        