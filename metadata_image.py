import os
from iptcinfo3 import IPTCInfo
import piexif

"""# **Model**"""

def add_keyword_xmp(image_path, keyword_list):
    try:
        keyword = keyword_list[0]
        for i in range(1, len(keyword_list)):
            keyword += ',' + keyword_list[i]
        os.system(f'exiftool -XMP:Subject+=" {keyword}" "{image_path}"')
        print(f"Ключевое слово '{keyword}' добавлено к метаданным XMP {image_path}")
    except Exception as e:
        print(f"Ошибка при добавлении ключевого слова к метаданным XMP {image_path}: {str(e)}")

# Функция для добавления ключевых слов в метаданные EXIF
def add_keywords_to_image_exif(image_path, keywords):
    try:
        # Загрузка существующих метаданных EXIF
        exif_dict = piexif.load(image_path)

        # Извлечение существующих ключевых слов
        existing_keywords = exif_dict["Exif"].get(piexif.ExifIFD.UserComment, b"").decode("utf-8")
        existing_keywords_list = existing_keywords.split(",") if existing_keywords else ['ASCII  ']
        
        # Добавление новых ключевых слов к существующим
        existing_keywords_list.extend(keywords)

        # Объединение ключевых слов обратно в строку
        keyword_str = " ".join(existing_keywords_list)
        exif_ifd = {piexif.ExifIFD.UserComment: keyword_str.encode()}
        exif_dict = {"0th": {}, "Exif": exif_ifd, "1st": {},
                "thumbnail": None, "GPS": {}}
        #exif_dat = piexif.dump(exif_dict)
        # Кодирование ключевых слов в байты и обновление метаданных EXIF
        #exif_dict["Exif"][piexif.ExifIFD.UserComment] = keyword_str.encode('utf-8')

        # Преобразование метаданных EXIF обратно в двоичный формат
        exif_bytes = piexif.dump(exif_dict)

        # Вставка обновленных метаданных EXIF в файл изображения
        piexif.insert(exif_bytes, image_path)

        print(f"Ключевые слова '{keywords}' добавлены к метаданным EXIF.")
    except Exception as e:
        print(f"Произошла ошибка при добавлении ключевых слов к метаданным EXIF: {str(e)}")

# Функция для добавления ключевых слов в метаданные IPTC
def add_keywords_to_image_iptc(image_path, keywords):
    try:
        info = IPTCInfo(image_path)
        existing_keywords = info['keywords']
        # Добавление новых ключевых слов к существующим
        
        for keyword in keywords:
            if keyword not in existing_keywords:
                existing_keywords.append(keyword)
        # Сохранение обновленных метаданных IPTC
        info['keywords'] = existing_keywords
        info.save()
    except Exception as e:
        print(f"Произошла ошибка при добавлении ключевых слов к метаданным IPTC: {str(e)}")

# Функция для тегирования изображений в зависимости от выбранного метода
def tag_images(filename, keywords, method):
    tagged_images = []  # Список для хранения путей к тегированным изображениям
 
    try:
        if method == 'XMP':           
            if filename.endswith(('.jpg', '.jpeg', '.png', '.JPG')):
                add_keyword_xmp(filename, keywords)
                tagged_images.append(filename)
        elif method == 'EXIF':
            if filename.endswith(('.jpg', '.jpeg', '.png', '.JPG')):
                add_keywords_to_image_exif(filename, keywords)
                tagged_images.append(filename)
        elif method == 'IPTC':
            if filename.endswith(('.jpg', '.jpeg', '.png', '.JPG')):
                add_keywords_to_image_iptc(filename, keywords)
                tagged_images.append(filename)
        elif method == 'All':
            for m in ['XMP', 'EXIF', 'IPTC']:
                if filename.endswith(('.jpg', '.jpeg', '.png', '.JPG')):
                    if m == 'XMP':                            
                        add_keyword_xmp(filename, keywords)
                    elif m == 'EXIF':
                        add_keywords_to_image_exif(filename, keywords)
                    elif m == 'IPTC':
                        add_keywords_to_image_iptc(filename, keywords)
                    tagged_images.append(filename)

        else:
            print("Выбран неверный метод.")
              
    except Exception as e:
        print(f"Ошибка: {e}")
    
