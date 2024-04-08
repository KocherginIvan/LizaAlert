import torch
import LizaAlert.settings as settings
import LizaAlert.grounding_dino_parser as grounding_dino_parser
import LizaAlert.detections_draw as detections_draw
import LizaAlert.metadata_image as metadata_image
import gradio as gr
from groundingdino.util.inference import load_model
import os

os.system('fuser -k 7860/tcp')
model = load_model("groundingdino/config/GroundingDINO_SwinT_OGC.py", "weights/groundingdino_swint_ogc.pth")

promt_start = settings.build_promt_start()
def tegs(files, promt_list):
  tegs_dict, lister_draw = grounding_dino_parser.get_tegs(
                        files,
                        promt_list,
                        model
                        )
  return tegs_dict, lister_draw

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

def text_to_promt(promter, files, check, Treshold, check1):
  import re
  promt = ''
  for keyword in promter.split("."):
    t = keyword.strip()
    promt += t + ' . '
  promt_list = re.split(r'\ . ', promt)
  promt_list.pop()
  promt_list_rus = settings.promt_to_rus(promt_list)
  if check1 == True:
    tegs_dict, lister_draw = tegs_one(files, promt_list)
    figur = draw(lister_draw, promt_list_rus)
  else:
    if check == True:
      tegs_dict, lister_draw = tegs_test(files, promt_list, Treshold)
      figur = draw_test(lister_draw, promt_list_rus)
    else:
      tegs_dict, lister_draw = tegs(files, promt_list)
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
    text_1 += i + ' \n'\
  
  torch.cuda.empty_cache()
  return text_1, figur

def text_to_promt_zip(promter, files, check):
  import re
  promt = ''
  for keyword in promter.split("."):
    t = keyword.strip()
    promt += t + ' . '
  promt_list = re.split(r'\ . ', promt)
  promt_list.pop()
  if check == True:
    tegs_dict, _ = tegs_one(files, promt_list)
  else:
    tegs_dict, _ = tegs(files, promt_list)
  zip_file = zip_files(tegs_dict)

  torch.cuda.empty_cache()
  return zip_file

with gr.Blocks() as iface:
    gr.Markdown("Тегирование изображений")
    promt_input = gr.Textbox(f'{promt_start}', label='Promt')
    
    with gr.Row():
      file_input = gr.File(file_count="multiple")
      with gr.Column():
        checkbox_test = gr.Checkbox(label='Режим подбора параметров')
        checkbox_one = gr.Checkbox(label='Режим одиночных проптов')
        treshold_slider = gr.Slider(0, 1, value=0.35, label="Treshold")
        tegs_button = gr.Button("Показать тегированные изображения")
        tegs_download_button = gr.Button("Скачать тегированные изображения")
        
    with gr.Row():
      file_output = gr.File()
      tegs_output = gr.Textbox(label='Словарь тегов')

    image_output = gr.Gallery(columns = 4, height = 960)
    tegs_button.click(text_to_promt, inputs=[promt_input, file_input, checkbox_test, treshold_slider, checkbox_one], outputs=[tegs_output, image_output])
    tegs_download_button.click(text_to_promt_zip, inputs = [promt_input, file_input, checkbox_one, treshold_slider],  outputs=[file_output])

iface.launch(server_port = 7860, root_path ='/app')

if __name__ == "__main__":
    main()