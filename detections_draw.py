import webcolors
import matplotlib.colors as pltc
import numpy as np
from PIL import Image, ImageDraw
import torch
import matplotlib.pyplot as plt
import LizaAlert.settings as settings
from groundingdino.util.inference import load_image
import io


def fig2img(fig): 
    buf = io.BytesIO() 
    fig.savefig(buf) 
    buf.seek(0) 
    img = Image.open(buf) 
    return img 

def all_colors(promt_list):
  colors = [k for k,v in pltc.cnames.items()]
  col = [2, 3, 9, 10, 11, 13, 14, 15, 17, 19, 21, 23, 25, 28, 30, 40, 48, 51, 55, 54, 68, 96, 106, 60, 52, 142, 120, 125, 117, 100, 80, 71]
  all_colors = []
  for i in col:
    all_colors.append(colors[i])
  class_color_1 = {}
  j = 0
  for i in promt_list: 
    if j != len(col):
      class_color_1[i] = all_colors[j]
      j += 1
    else:
      j = 0
      class_color_1[i] = all_colors[j]     
  class_color = {}
  for i in promt_list:
    class_color[i] = tuple(webcolors.name_to_rgb(class_color_1[i]))
  return class_color, class_color_1

def preprocess_caption(caption: str
                       ) -> str:
  result = caption.lower().strip()
  if result.endswith("."):
      return result
  return result + "."
  
def transform_bbox_coords(bbox
                          ):
  '''
  Трансформация координат ббокса из фотмата х_центра, у_центра, ширина, высота в x_min, y_min, x_max, y_max.
  '''
  x_cent, y_cent, width, height = bbox
  x_min = int(x_cent - width/2)
  y_min = int(y_cent - height/2)
  x_max = int(x_cent + width/2)
  y_max = int(y_cent + height/2)
  return [x_min, y_min, x_max, y_max]

def color_title(labels,
                colors,
                textprops = {'size':'large'},
                ax = None,
                y = 1.013,
                precision = 10**-2
                ):
  "Creates a centered title with multiple colors. Don't change axes limits afterwards."
  if ax == None:
      ax = plt.gca()
  plt.gcf().canvas.draw()
  transform = ax.transAxes # use axes coords
  # initial params
  xT = 0 # where the text ends in x-axis coords
  shift = 0 # where the text starts
  # for text objects
  text = dict()
  while (np.abs(shift - (1-xT)) > precision) and (shift <= xT) :
      x_pos = shift
      for label, col in zip(labels, colors):
          try:
              text[label].remove()
          except KeyError:
              pass
          text[label] = ax.text(x_pos, y, label,
                      transform = transform,
                      ha = 'left',
                      color = col,
                      **textprops)
          x_pos = text[label].get_window_extent()\
                  .transformed(transform.inverted()).x1
      xT = x_pos # where all text ends
      shift += precision/2 # increase for next iteration
      if x_pos > 1: # guardrail
          break

def display_images_grid(images,
                        images_titles,
                        imagesNumber_per_row,
                        class_color_1,
                        show_indexes=True,
                        startIndex=0,
                        showTitle = True,
                        figsize_ratio=(12, 12),
                        facecolor='black',
                        cmap=None):

  '''
  функция вывода изображений массива в табличной форме с указанием индекса изображения
  '''
  img_bbox_list = []
  n_images = len(images)
  plt.figure(figsize=(figsize_ratio[0], figsize_ratio[1]), facecolor=facecolor)
  
  for i in range(n_images):
      plt.figure(figsize=(figsize_ratio[0], figsize_ratio[1]), facecolor=facecolor)
      img = images[i]
      plt.imshow(img, cmap=cmap)
      plt.axis('off')
      try:
        if showTitle:
          color = []
          for j in images_titles[i]:
            color.append(class_color_1[j])
          color_title(images_titles[i],color)
        if show_indexes:
            plt.text(0.5, 0.9, 'index: '+str(startIndex+i), color='magenta', horizontalalignment='center', verticalalignment='center', fontsize=15, fontweight='bold', transform=ax.transAxes)
      except:
         print('')
      plt.tight_layout()
      fig = plt.gcf()
      plt.show()
      img_bbox_list.append(fig2img(fig))
  return img_bbox_list
  
def draw_img_1(img_list,
               boxes_list,
               phrases,
               phrases_2,
               promter,
               facecolor = 'grey',
               draw_labels = True
               ):
  class_color, class_color_1 = all_colors(promter)
  imagePIL_list = []
  phrases_3 = []  
  for i in range(len(img_list)):
      phrases_3.append(phrases_2[i])
      image_source, image = load_image(img_list[i])
      imagePIL = Image.fromarray(image_source)
 
      bboxes = (boxes_list[i]*torch.Tensor(imagePIL.size).tile((boxes_list[i].size()[0], int(boxes_list[i].size()[1]/2)))).to(dtype=torch.int16).tolist()        

      draw = ImageDraw.Draw(imagePIL)
      try:
        for j in range(len(bboxes)):
            bbox = transform_bbox_coords(bboxes[j])
            color = class_color[phrases[i][j]]
            draw.rectangle(bbox, outline=color, width=5)
      except:
         print(phrases[i])
      imagePIL_list.append(imagePIL)
  figu = display_images_grid(imagePIL_list, phrases_3, 1,class_color_1, show_indexes= False,facecolor=facecolor )
  return figu

def draw_img(img_list, boxes_list, promt, phrases_2, facecolor, promter):   
   img_bbox_lister = draw_img_1(img_list, boxes_list, promt, phrases_2, promter, facecolor)
   return img_bbox_lister

def visualize_detections(
    img_list, boxes, classes, images_titles, scores, promter, figsize=(14, 9), linewidth=1, facecolor = 'black', showTitle = True
):
    """Визуализация обнаружения"""
    _, class_color_1 = all_colors(promter)
    fig_list = []
    for i in range(len(img_list)):
      img = Image.open(img_list[i])
      image = np.array(img, dtype=np.uint8)
      
      plt.figure(facecolor = 'grey')
      plt.imshow(image)
      plt.axis("off")
      ax = plt.gca()
      try:
        bboxes = (boxes[i]*torch.Tensor(img.size).tile((boxes[i].size()[0], int(boxes[i].size()[1]/2)))).to(dtype=torch.int16).tolist()    
        for box, _cls, score in zip(bboxes, classes[i], scores[i]):
            text = "{}: {:.2f}".format(_cls, score)          
            x1, y1, x2, y2 = transform_bbox_coords(box)
            w, h = x2 - x1, y2 - y1
            patch = plt.Rectangle(
                [x1, y1], w, h, fill=False, edgecolor=class_color_1[_cls], linewidth=linewidth
            )
            ax.add_patch(patch)
            ax.text(
                x1+15,
                y1-17,
                text,
                bbox={"facecolor": class_color_1[_cls], "alpha": 0.4},
                clip_box=ax.clipbox,
                clip_on=False,
            )
      except:
         a=0
      fig = plt.gcf()
      plt.show()
      figure1 = fig2img(fig)
      fig_list.append(figure1)
    return fig_list
def draw_test(img_list, boxes_list, phrase_list, phrases_2, logits, facecolor, promter):   
   _, promt_list, _, _ = settings.promter(promter)
   figu = visualize_detections(img_list, boxes_list, phrase_list, phrases_2, logits, promt_list, facecolor)
   return figu