import torch
from torchvision.models import resnet50
import LizaAlert.settings as settings
import LizaAlert.grounding_dino_parser as grounding_dino_parser
import LizaAlert.detections_draw as detections_draw
import LizaAlert.metadata_image as metadata_image
import LizaAlert.face_reco as face_reco
import LizaAlert.classification_season as classification_season
import gradio as gr
from groundingdino.util.inference import load_model
import os
from PIL import Image
import numpy as np
import cv2
import re

os.system('fuser -k 7860/tcp')
model = load_model("groundingdino/config/GroundingDINO_SwinT_OGC.py", "weights/groundingdino_swint_ogc.pth")
model_path_list = ['/home/lizaalert/ProjectLiza/GroundingDINO/resnet50_citi_out.pth', '/home/lizaalert/ProjectLiza/GroundingDINO/resnet50_epoch_20.pth', '/home/lizaalert/ProjectLiza/GroundingDINO/resnet50_daytime.pth']
path_out = '/home/lizaalert/ProjectLiza/Photo'
promt_start = settings.build_promt_start()
# Загрузка обученной модели season
model_season = resnet50()
model_season.load_state_dict(torch.load(model_path_list[0]))
model_season.eval()
model_city = resnet50()
model_city.load_state_dict(torch.load(model_path_list[1]))
model_city.eval()
model_day = resnet50()
model_day.load_state_dict(torch.load(model_path_list[2]))
model_day.eval()

def print_phrases_true(phrases_true):
  with open('/home/lizaalert/ProjectLiza/phrases_true.txt', 'a') as myfile:
    myfile.write(f'{phrases_true}')
    myfile.close()
def ff(files):
	str_f = files[0]
	for i in range(1, len(files)):
		str_f = str_f + ',' + files[i]
	return str_f
def clear(list_c):
  if type(list_c)!= list:
    list_c = re.split(r'\,',list_c)
  for i in list_c:
    os.remove(i)
    dir_name  = re.split(r'\/', i)
    fdm = '/'
    for j in range(len(dir_name)-1):
      fdm = fdm + dir_name[j] + '/'
    if dir_name[-2] != 'Photo':
      os.rmdir(fdm)

def resize(img_path_list):
  file_out_list = []
  for img_path in img_path_list:
    file_name_0 = re.split(r'\/', img_path)[-1]
    file_name = re.split(r'\ . ', file_name_0)[-1]
    file_name_out = f'{path_out}/{file_name}.jpg'
    # Прочитать исходное изображение
    img = cv2.imread(img_path)
    # Определить новый размер
    new_size = (800, 800)
    # Определить пропорциональное изменение
    h, w = img.shape[:2]
    h_ratio = new_size[1] / h
    w_ratio = new_size[0] / w
    # Выбрать минимальное соотношение для масштабирования
    ratio = min(h_ratio, w_ratio)
    # Новый размер после пропорционального изменения
    new_h = int(h * ratio)
    new_w = int(w * ratio)
    # Определить смещение для центрирования
    top = (new_size[1] - new_h) // 2
    left = (new_size[0] - new_w) // 2
    # Изменить размер изображения с сохранением пропорций
    resized_img = cv2.resize(img, (new_w, new_h))
    # Создать новое черное изображение
    new_img = np.zeros(new_size + (3,), np.uint8)
    new_img[top:top + new_h, left:left + new_w] = resized_img
    # Вывести измененное изображение
    #cv2.imshow('Resized Image', new_img)
    cv2.imwrite(file_name_out, new_img)
    file_out_list.append(file_name_out)
  return file_out_list

def tegs(files, promt_list):
  tegs_dict, lister_draw, phrases_true = grounding_dino_parser.get_tegs(
                        files,
                        promt_list,
                        model
                        )
  return tegs_dict, lister_draw, phrases_true

def tegs_test(files, promt_list, Treshold):
  tegs_dict, lister_draw = grounding_dino_parser.get_tegs_test(
                        files,
                        promt_list,
                        Treshold,
                        model
                        )
  return tegs_dict, lister_draw

def tegs_one(files, promt_list):
  tegs_dict, lister_draw = grounding_dino_parser.get_tegs_one_for_step(
                        files,
                        promt_list,
                        model
                        )
  return tegs_dict, lister_draw

def draw_test(lister_draw, promt_list):
  fig = detections_draw.visualize_detections(lister_draw['img_list'],
                                      lister_draw['box_list'],
                                      lister_draw['phrase_list'],
                                      lister_draw['phrase_1_list'],
                                      lister_draw['logits'],
                                      promter = promt_list,
                                      facecolor = 'grey'
                                      )
  return fig

def draw(lister_draw, promt_list):
  fig = detections_draw.draw_img(lister_draw['img_list'],
                                 lister_draw['box_list'],
                                 lister_draw['phrase_list'],
                                 lister_draw['phrase_1_list'],
                                 promter = promt_list,
                                 facecolor = 'grey'
                                )
  return fig

def reco(files, tegs_dict, lister_draw, jit, tolerance, number_of_times_to_upsample, accuracy, check1):
  for i in range(len(lister_draw['img_list'])):
    a = str(files[i])
    faces = face_reco.Faces_Recognition(a)
      # 'hog'- CPU, 'cnn'- GPU
    faces.loc_model = 'hog'
    faces.jit = jit
    faces.tolerance = tolerance
    faces.number_of_times_to_upsample = number_of_times_to_upsample
    faces.accuracy = accuracy
    rez = faces.recognition()
    box = []
    phrase = []
    logits = []
    for k in rez:
      if box == []:
        imagePIL = Image.open(a)
        box = torch.as_tensor([rez[k][0][0]/imagePIL.size[0], rez[k][0][1]/imagePIL.size[1], rez[k][0][2]/imagePIL.size[0], rez[k][0][3]/imagePIL.size[1]]).resize_(1, 4)
      else:
        imagePIL = Image.open(a)
        bbox = torch.as_tensor([rez[k][0][0]/imagePIL.size[0], rez[k][0][1]/imagePIL.size[1], rez[k][0][2]/imagePIL.size[0], rez[k][0][3]/imagePIL.size[1]]).resize_(1, 4)
        box = torch.cat((box, bbox.resize_(1, 4)), 0)
      phrase.append(k)
      logits.append(rez[k][2])

    try:
      lister_draw['box_list'][i] = torch.cat((lister_draw['box_list'][i], box), 0)
      for j in phrase:
        lister_draw['phrase_list'][i].append(j)
        if j in lister_draw['phrase_1_list'][i]:
          print('')
        else:
          lister_draw['phrase_1_list'][i].append(j)
        if j in tegs_dict[files[i]]:
          print('')
        else:  
          tegs_dict[files[i]].append(j)
      for j in logits:
        aa = torch.as_tensor(j).resize(1)
        if check1 == True:
          lister_draw['logits'][i]. append(j)
        else:
          lister_draw['logits'][i] = torch.cat((lister_draw['logits'][i],aa))
    except:
      print('')
  return tegs_dict, lister_draw

def season(files, tegs_dict, lister_draw):
  a = 0
  label_mapping_list  = [{'Холодный сезон': 0, 'Теплый сезон': 1},
                         {'В городе': 0, 'Загород/Парк': 1},
                         {'Светлое время суток': 0, 'Темное время суток': 1}]
  for file in files:
    b = 0
    for model_classification in model_list:
      try:
        cc = classification_season.classify_images(file, model_classification, label_mapping_list[b])
        if cc in lister_draw['phrase_1_list'][a]:
          d = 0
        else:
          lister_draw['phrase_1_list'][a].append(cc)
        if cc in tegs_dict[file]:
          d = 0
        else:
          tegs_dict[file].append(cc)
      except:
        print('')
      b += 1
    a += 1
  return tegs_dict, lister_draw

def zip_files(tegs_dict):
      from zipfile import ZipFile
      for files in tegs_dict:
         metadata_image.tag_images(files, tegs_dict[files], 'All')
      with ZipFile("tagged_images.zip", "w") as zipObj:
          for idx in tegs_dict:
              dd = idx.split("/")
              idx1 = dd[-1]
              zipObj.write(idx, str(idx1))
      return 'tagged_images.zip'

def text_to_promt(promter, files, check, Treshold, check1, jit, tolerance, number_of_times_to_upsample, accuracy):
  files_list = resize(files)
  import re
  promt = ''
  for keyword in promter.split("."):
    t = keyword.strip()
    promt += t + ' . '
  promt_list = re.split(r'\ . ', promt)
  promt_list.pop()
  promt_list_rus = settings.promt_to_rus(promt_list)
  if check1 == True:
    tegs_dict, lister_draw = tegs_one(files_list, promt_list)
    tegs_dict, lister_draw = reco(files_list, tegs_dict, lister_draw, jit, tolerance, number_of_times_to_upsample, accuracy, check1)
    tegs_dict, lister_draw = season(files_list, tegs_dict, lister_draw)
    figur = draw_test(lister_draw, promt_list_rus)
  else:
    if check == True:
      tegs_dict, lister_draw = tegs_test(files_list, promt_list, Treshold)
      tegs_dict, lister_draw = reco(files_list, tegs_dict, lister_draw, jit, tolerance, number_of_times_to_upsample, accuracy, check1)
      tegs_dict, lister_draw = season(files_list, tegs_dict, lister_draw)
      figur = draw_test(lister_draw, promt_list_rus)
    else:
      tegs_dict, lister_draw, phrases_true = tegs(files_list, promt_list)
      print_phrases_true(phrases_true)
      tegs_dict, lister_draw = reco(files_list, tegs_dict, lister_draw, jit, tolerance, number_of_times_to_upsample, accuracy, check1)
      tegs_dict, lister_draw = season(files_list, tegs_dict, lister_draw)
      
      figur = draw(lister_draw, promt_list_rus)
  text = []
  for i in tegs_dict:
    file_name = re.split(r'\/', i)[-1]
    teg = ''
    for j in tegs_dict[i]:
      teg += j + ' '
    text.append(f'Имя файла: {file_name} - Теги: {teg}')
  text_1 = ''
  for i in text:
    text_1 += i + ' \n'
  clear(files_list)
  torch.cuda.empty_cache()
  return text_1, figur

def text_to_promt_zip(promter, files, check, Treshold, jit, tolerance, number_of_times_to_upsample, accuracy, check1):
  import re
  promt = ''
  for keyword in promter.split("."):
    t = keyword.strip()
    promt += t + ' . '
  promt_list = re.split(r'\ . ', promt)
  promt_list.pop()
  if check == True:
    tegs_dict, lister_draw = tegs_one(files, promt_list)
    tegs_dict, lister_draw =reco(files, tegs_dict, lister_draw, jit, tolerance, number_of_times_to_upsample, accuracy, False)
    tegs_dict, lister_draw = season(files, tegs_dict, lister_draw)
  else:
    tegs_dict, lister_draw, phrases_true = tegs(files, promt_list)
    tegs_dict, lister_draw =reco(files, tegs_dict, lister_draw, jit, tolerance, number_of_times_to_upsample, accuracy, False)
    tegs_dict, lister_draw = season(files, tegs_dict, lister_draw)
  zip_file = zip_files(tegs_dict)
  
  torch.cuda.empty_cache()
  return zip_file

with gr.Blocks(delete_cache = (600,600)) as iface:
    gr.Markdown("Тегирование изображений")
    promt_input = gr.Textbox(f'{promt_start}', label='Promt', visible = False)

    with gr.Row():
      file_input = gr.File(file_count="multiple")
      file_list = gr.Textbox(visible = False)
      with gr.Column():
        checkbox_test = gr.Checkbox(label='Режим подбора параметров', visible = False)
        checkbox_one = gr.Checkbox(label='Режим одиночных промптов', visible = False)
        treshold_slider = gr.Slider(0, 1, value=0.35, step = 0.01, label="Treshold", visible = False)
        accuracy_slider = gr.Slider(0, 1, value=0.7, step = 0.1, label="accuracy", visible = False)
        jit_slider = gr.Slider(0, 100, value = 10, step = 1, label = 'jit: Сколько раз повторять выборку лица при расчете кодировки. Чем выше, тем точнее, но медленнее (т. е. 100 — в 100 раз медленнее)', visible = False)
        tolerance_slider = gr.Slider(0, 1 , value = 0.55, step = 0.01, label = 'tolerance: Какое расстояние между лицами, чтобы считать его совпадающим.Нижний более строгий.', visible = False)
        number_of_times_to_upsample_slider = gr.Slider(1, 10, value = 1, step = 1, label = 'number_of_times_to_upsample: Cколько раз повышать дискретизацию изображения в поисках лиц. Чем выше число, тем меньше лица.', visible = False )
        tegs_button = gr.Button("Показать тегированные изображения")
        tegs_download_button = gr.Button("Скачать тегированные изображения")

    with gr.Row():
      file_output = gr.File()
      tegs_output = gr.Textbox(label='Словарь тегов')

    file_input.clear(clear, inputs = file_list)
    file_input.upload(ff, inputs = file_input, outputs = file_list)
    image_output = gr.Gallery(columns = 4, height = 960)
    tegs_button.click(text_to_promt, inputs=[promt_input, file_input, checkbox_test, treshold_slider, checkbox_one, jit_slider, tolerance_slider, number_of_times_to_upsample_slider, accuracy_slider], outputs=[tegs_output, image_output])
    tegs_download_button.click(text_to_promt_zip, inputs = [promt_input, file_input, checkbox_test, treshold_slider, jit_slider, tolerance_slider, number_of_times_to_upsample_slider, accuracy_slider],  outputs=[file_output])
    
    gr.HTML(value="<div style='margin-top: 0rem, margin-bottom: 0rem, align: center'><center><p style='margin-top: 1rem, margin-bottom: 1rem'>[ <a href='https://lizaalert.host/advanced/' _target='blank'>Рассширенная версия</a> ]</p></center></div>")

iface.launch(server_port = 7860, root_path ='/app')

if __name__ == "__main__":
    main()