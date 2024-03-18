import os
import torch
from typing import Tuple, List
import bisect
import matplotlib.pyplot as plt
import numpy as np
import math
import groundingdino.datasets.transforms as T
from groundingdino.util.utils import get_phrases_from_posmap
from groundingdino.util.inference import  load_image
import LizaAlert.settings as settings
import re

def preprocess_caption(caption: str) -> str:
  result = caption.lower().strip()
  if result.endswith("."):
      return result
  return result + "."

def prepredict_1(boxes,
                logits,
                phrases,
                text_prompt_list,
                BOX_TRESHOLD_list
                ):
  bbox = []
  log = []
  phra =[]
  for i in range(len(text_prompt_list)):
    for j in range(len(phrases)):
      if phrases[j] == text_prompt_list[i]:
        if logits[j] >= BOX_TRESHOLD_list[i]:
          bbox.append(boxes[j])
          log.append(logits[j])
          phra.append(phrases[j])
  bbox = np.array(bbox)
  log = np.array(log)
  bbox = torch.from_numpy(bbox)
  log = torch.from_numpy(log)
  return bbox, log, phra

def predict_1(
        model,
        image: torch.Tensor,
        caption: str,
        box_threshold: float,
        text_threshold: float,        
        device: str = "cuda",
        remove_combined: bool = False
  ) -> Tuple[torch.Tensor, torch.Tensor, List[str]]:
  caption = preprocess_caption(caption=caption)
  model = model.to(device)
  image = image.to(device)
  with torch.no_grad():
      outputs = model(image[None], captions=[caption])
  prediction_logits = outputs["pred_logits"].cpu().sigmoid()[0]  # prediction_logits.shape = (nq, 256)
  prediction_boxes = outputs["pred_boxes"].cpu()[0]  # prediction_boxes.shape = (nq, 4)
  mask = prediction_logits.max(dim=1)[0] > box_threshold
  logits = prediction_logits[mask]  # logits.shape = (n, 256)
  boxes = prediction_boxes[mask]  # boxes.shape = (n, 4)

  tokenizer = model.tokenizer
  tokenized = tokenizer(caption)

  if remove_combined:
      sep_idx = [i for i in range(len(tokenized['input_ids'])) if tokenized['input_ids'][i] in [101, 102, 1012]]

      phrases = []
      for logit in logits:
          max_idx = logit.argmax()
          insert_idx = bisect.bisect_left(sep_idx, max_idx)
          right_idx = sep_idx[insert_idx]
          left_idx = sep_idx[insert_idx - 1]
          phrases.append(get_phrases_from_posmap(logit > text_threshold, tokenized, tokenizer, left_idx, right_idx).replace('.', ''))
  else:
      phrases = [
          get_phrases_from_posmap(logit > text_threshold, tokenized, tokenizer).replace('.', '')
          for logit
          in logits
      ]
  return boxes, logits.max(dim=1)[0], phrases

def parser_tegs(img_list, model, promt, promt_list, BOX_TRESHOLD_list):
  
  bbox = BOX_TRESHOLD_list[0]
  for i in range(1, len(BOX_TRESHOLD_list)):
    bbox_1 = BOX_TRESHOLD_list[i]
    if bbox > bbox_1:
      bbox = bbox_1
  BOX_TRESHOLD = bbox
  TEXT_TRESHOLD = bbox  
  lister = {}
  lister_draw = {}
  boxes_list = []
  phrases_2 = []
  phrases_3 = []
  img_no_box = []
  logit_1 = []
  for i in img_list:    
    _, image = load_image(i)
    boxes, logits, phrases = predict_1(
        model=model,
        image=image,
        caption=promt,
        box_threshold=BOX_TRESHOLD,
        text_threshold=TEXT_TRESHOLD,        
        )
    boxes_1, logit, phrases = prepredict_1(boxes, logits, phrases, promt_list, BOX_TRESHOLD_list)
    if boxes == []:
      print(f'Файл {i} не распознана не одна сущность')
      img_no_box.append(i)
    else:
      settings.promt_to_rus(promt_list)
      phrases_1 = list(set(settings.promt_to_rus(phrases)))
      lister[i] = []
      lister[i] = phrases_1
      phrases_2.append(phrases_1)
      phrases_3.append(settings.promt_to_rus(phrases))
      boxes_list.append(boxes_1)
      logit_1.append(logit)
    lister_draw['img_list'] = img_list
    lister_draw['box_list'] = boxes_list
    lister_draw['phrase_list'] = phrases_3
    lister_draw['phrase_1_list'] = phrases_2
    lister_draw['logits'] = logit_1
  return lister, lister_draw

def get_tegs(img_list, promt_1, model):
    promt, promt_list, BOX_TRESHOLD_list = settings.promter(promt_1)
    lister, lister_draw = parser_tegs(img_list, model, promt, promt_list, BOX_TRESHOLD_list)
    return lister, lister_draw    
def get_tegs_test(img_list, promt_1, TRESHOLD, model):
    promt, promt_list, BOX_TRESHOLD_list = settings.promter_test(promt_1, TRESHOLD)
    lister, lister_draw = parser_tegs(img_list, model, promt, promt_list, BOX_TRESHOLD_list)
    return lister, lister_draw