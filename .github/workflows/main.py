import config
import grounding_dino_parser
import detections_draw
import re
import gradio as gr
from groundingdino.util.inference import load_model, load_image

model = load_model("~/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py", '~/GroundingDINO/weights')


promt_start = config.build_promt_start()
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

def text_to_promt(promter, files, check, Treshold):
  import re
  promt = ''
  for keyword in promter.split("."):
    t = keyword.strip()
    promt += t + ' . '
  promt_list = re.split(r'\ . ', promt)
  promt_list.pop()
  if check == True:
    tegs_dict, lister_draw = tegs_test(files, promt_list, Treshold)
    figur = draw_test(lister_draw, promt_list)
  else:
    tegs_dict, lister_draw = tegs(files, promt_list)
    figur = draw(lister_draw, promt_list)
  return tegs_dict, figur
  
with gr.Blocks() as iface:
    gr.Markdown("Тегирование изображений")
    promt_input = gr.Textbox(f'{promt_start}', label='Promt')
    file_input = gr.File(file_count="multiple")
    checkbox_test = gr.Checkbox(label='Режим подбора параметров')
    tegs_button = gr.Button("Показать тегированные изображения")
    treshold_slider = gr.Slider(0, 1, value=0.35, label="Treshold")
    tegs_output = gr.Textbox(label='Словарь тегов')
    image_output = gr.Gallery(columns = 4, height = 960)
    tegs_button.click(text_to_promt, inputs=[promt_input, file_input, checkbox_test, treshold_slider], outputs=[tegs_output, image_output])
iface.launch()

if __name__ == "__main__":
    main()