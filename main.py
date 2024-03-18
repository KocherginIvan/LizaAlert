import LizaAlert.settings as settings
import LizaAlert.grounding_dino_parser as grounding_dino_parser
import LizaAlert.detections_draw as detections_draw
import LizaAlert.xmp_lizaalert as xmp_lizaalert
import re
import gradio as gr
from groundingdino.util.inference import load_model

model = load_model("~/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py", '~/GroundingDINO/weights')


promt_start = settings.build_promt_start()
def main():
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
      xmp_lizaalert.teg_XMP(tegs_dict)
      xmp_lizaalert.teg_iptc(tegs_dict)
      with ZipFile("tmp.zip", "w") as zipObj:
          for idx in tegs_dict:
              dd = idx.split("/")
              idx1 = dd[-1]
              zipObj.write(idx, str(idx1))
      return "tagged_images.zip"

  def text_to_promt(promter, files, check, Treshold):
    import re
    promt = ''
    for keyword in promter.split("."):
      t = keyword.strip()
      promt += t + ' . '
    promt_list = re.split(r'\ . ', promt)
    promt_list.pop()
    promt_list_rus = settings.promt_to_rus(promt_list)
    if check == True:
      tegs_dict, lister_draw = tegs_test(files, promt_list, Treshold)
      figur = draw_test(lister_draw, promt_list)
    else:
      tegs_dict, lister_draw = tegs(files, promt_list)
      figur = draw(lister_draw, promt_list_rus)
    text1 = []
    for t in tegs_dict:    
      dd = t.split("/")
      id1 = dd[-1]
      tete = tegs_dict[t][0]
      for i in range(1, len(tegs_dict[t])):
        tete += ' ' + tegs_dict[t][i]
      text1.append(f'Файл:{id1} Теги: {tete}')
    text = text1[0]
    for t in range(1, len(text1)):
      text += text 
    return text1, figur

  def text_to_promt_zip(promter, files, check, Treshold):
    import re
    promt = ''
    for keyword in promter.split("."):
      t = keyword.strip()
      promt += t + ' . '
    promt_list = re.split(r'\ . ', promt)
    promt_list.pop()
    tegs_dict, _ = tegs(files, promt_list)
    zip_file = zip_files(tegs_dict)
    return zip_file

  with gr.Blocks() as iface:
      gr.Markdown("Тегирование изображений")
      promt_input = gr.Textbox(f'{promt_start}', label='Promt')
      file_input = gr.File(file_count="multiple")
      checkbox_test = gr.Checkbox(label='Режим подбора параметров')
      tegs_button = gr.Button("Показать тегированные изображения")
      tegs_download_button = gr.Button("Скачать тегированные изображения")
      treshold_slider = gr.Slider(0, 1, value=0.35, label="Treshold")
      file_output = gr.File()
      tegs_output = gr.Textbox(label='Словарь тегов')
      image_output = gr.Gallery(columns = 4, height = 960)
      tegs_button.click(text_to_promt, inputs=[promt_input, file_input, checkbox_test, treshold_slider], outputs=[tegs_output, image_output])
      tegs_download_button.click(text_to_promt_zip, inputs = [promt_input, file_input, checkbox_test, treshold_slider], outputs=[file_output])
  iface.launch()

if __name__ == "__main__":
    main()