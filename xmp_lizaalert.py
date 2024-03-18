import piexif
from iptcinfo3 import IPTCInfo
import os
import shutil
from google.colab import files
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual
from time import sleep
from ipywidgets import interact_manual, Dropdown, Text

"""**Добавление метаданных XMP к изображению**"""

def teg_XMP(lister):
    for img in lister:
      tegs = ''
      exif_dict = piexif.load(img)
      for i in lister[img]:
        tegs += ' ' + i
      #tegs_b = bytes(tegs, 'utf-8')
      tegs_b = tegs.encode("utf-8")       
      exif_dict["Exif"][piexif.ExifIFD.UserComment] = tegs_b
      exif_bytes = piexif.dump(exif_dict)
      piexif.insert(exif_bytes, img)
      print(img)   
  
def teg_iptc(lister):
  for image_path in lister:
    info = IPTCInfo(image_path)
    existing_keywords = info['keywords']
    # Добавление новых ключевых слов, которых еще нет
    for keyword in lister[image_path]:
        if keyword not in existing_keywords:
            existing_keywords.append(keyword)
    # Установка ключевых слов в метаданных IPTC
    info['keywords'] = existing_keywords
    # Сохранение обновленных метаданных
    info.save()



