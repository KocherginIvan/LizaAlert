import os
from iptcinfo3 import IPTCInfo
import piexif

"""# **Model**"""

# Функция для добавления ключевого слова в метаданные XMP
def add_keyword_xmp(image_path, keyword):
    try:
        os.system(f'exiftool -XMP:Subject+=" {keyword}" "{image_path}"')
        #print(f"Ключевое слово '{keyword}' добавлено к метаданным XMP {image_path}")

        # Печать доступных ключевых слов XMP
        #print_available_keywords_xmp(image_path)
    except Exception as e:
        print(f"Ошибка при добавлении ключевого слова к метаданным XMP {image_path}: {str(e)}")

# Вспомогательная функция для печати доступных ключевых слов XMP
def print_available_keywords_xmp(image_path):
    try:
        # Получение доступных ключевых слов из метаданных XMP
        output = os.popen(f'exiftool -XMP:Subject "{image_path}"').read()
        keywords = output.split(": ")[1].split(", ")
        print("Доступные ключевые слова XMP:")
        print(" | ".join([f"{keyword}" for keyword in keywords]))
        print("\n" + "=" * 50 + "\n")
    except Exception as e:
        print(f"Ошибка при печати доступных ключевых слов XMP: {str(e)}")


# Функция для добавления ключевых слов в метаданные EXIF
def add_keywords_to_image_exif(image_path, keywords):
    try:
        # Загрузка существующих метаданных EXIF
        exif_dict = piexif.load(image_path)

        # Извлечение существующих ключевых слов
        existing_keywords = exif_dict["Exif"].get(piexif.ExifIFD.UserComment, b"").decode("utf-8")
        existing_keywords_list = existing_keywords.split(",") if existing_keywords else []

        # Добавление новых ключевых слов к существующим
        existing_keywords_list.extend(keywords)

        # Объединение ключевых слов обратно в строку
        keyword_str = ",".join(existing_keywords_list)

        # Кодирование ключевых слов в байты и обновление метаданных EXIF
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = keyword_str.encode('utf-8')

        # Преобразование метаданных EXIF обратно в двоичный формат
        exif_bytes = piexif.dump(exif_dict)

        # Вставка обновленных метаданных EXIF в файл изображения
        piexif.insert(exif_bytes, image_path)

        #print(f"Ключевые слова '{keywords}' добавлены к метаданным EXIF.")

        # Печать доступных ключевых слов EXIF
        #print_available_keywords_exif(image_path)
    except Exception as e:
        print(f"Произошла ошибка при добавлении ключевых слов к метаданным EXIF: {str(e)}")

# Вспомогательная функция для печати доступных ключевых слов EXIF
def print_available_keywords_exif(image_path):
    try:
        # Загрузка существующих метаданных EXIF
        exif_dict = piexif.load(image_path)

        # Извлечение существующих ключевых слов
        existing_keywords = exif_dict["Exif"].get(piexif.ExifIFD.UserComment, b"").decode("utf-8")
        existing_keywords_list = existing_keywords.split(",") if existing_keywords else []

        #print("Доступные ключевые слова EXIF:")
        #print(" | ".join([f"[{keyword}]" for keyword in existing_keywords_list]))
        #print("\n" + "=" * 50 + "\n")
    except Exception as e:
        print(f"Ошибка при печати доступных ключевых слов EXIF: {str(e)}")


# Функция для добавления ключевых слов в метаданные IPTC
def add_keywords_to_image_iptc(image_path, keywords):
    try:
        info = IPTCInfo(image_path)
        existing_keywords = info['keywords']

        # Преобразование ключевых слов в кодировку UTF-8
        keywords_utf8 = []
        for keyword in keywords:
            if isinstance(keyword, bytes):
                keywords_utf8.append(keyword.decode('utf-8'))
            elif isinstance(keyword, str):
                keywords_utf8.append(keyword)

        # Преобразование существующих ключевых слов к строковому формату
        existing_keywords_str = [kw.decode('utf-8') if isinstance(kw, bytes) else kw for kw in existing_keywords]

        # Добавление новых ключевых слов к существующим
        for keyword in keywords_utf8:
            if keyword not in existing_keywords_str:
                existing_keywords_str.append(keyword)

        # Преобразование обратно в байты для сохранения
        existing_keywords_bytes = [kw.encode('utf-8') if isinstance(kw, str) else kw for kw in existing_keywords_str]

        # Сохранение обновленных метаданных IPTC
        info['keywords'] = existing_keywords_bytes
        info.save()
        #print(f"Ключевые слова '{keywords}' добавлены к метаданным IPTC.")

        # Печать доступных ключевых слов IPTC
        #print_available_keywords_iptc(image_path)

    except Exception as e:
        print(f"Произошла ошибка при добавлении ключевых слов к метаданным IPTC: {str(e)}")

# Вспомогательная функция для печати доступных ключевых слов IPTC
def print_available_keywords_iptc(image_path):
    try:
        info = IPTCInfo(image_path)
        existing_keywords = info['keywords']
        existing_keywords_str = [f"[{kw.decode('utf-8')} ]" if isinstance(kw, bytes) else f"[{kw} ]" for kw in existing_keywords]
        print("Доступные ключевые слова IPTC:")
        print(" | ".join(existing_keywords_str))
        print("\n" + "=" * 50 + "\n")
    except Exception as e:
        print(f"Ошибка при печати доступных ключевых слов IPTC: {str(e)}")


# Функция для тегирования изображений в зависимости от выбранного метода
def tag_images(filename, keywords, method):
    tagged_images = []  # Список для хранения путей к тегированным изображениям
 
    try:
        if method == 'XMP':           
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                add_keyword_xmp(filename, keywords)
                tagged_images.append(filename)
        elif method == 'EXIF':
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                add_keywords_to_image_exif(filename, keywords)
                tagged_images.append(filename)
        elif method == 'IPTC':
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                add_keywords_to_image_iptc(filename, keywords)
                tagged_images.append(filename)
        elif method == 'All':
            for m in ['XMP', 'EXIF', 'IPTC']:
                if filename.endswith(('.jpg', '.jpeg', '.png')):
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
    
