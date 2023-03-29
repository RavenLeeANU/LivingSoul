from scipy.io import wavfile
import time
import sys
import numpy as np
import torch
import argparse
import onnxruntime as ort
from playsound import playsound

sys.path.append('MoeGoe')
from text import text_to_sequence
from utils import *
from commons import *

import os



def is_japanese(string):
    for ch in string:
        if ord(ch) > 0x3040 and ord(ch) < 0x30FF:
            return True
    return False


class TTSClient:
    def __init__(self, config):
        self.mode_path = os.path.join(config["tts_model_path"], config["tts_model"])
        self.config_path = os.path.join(config["tts_model_path"], config["tts_config"])

        self.args = self.get_args()
        self.hyper_params = get_hparams_from_file(self.args.cfg)
        self.ort_session = ort.InferenceSession(self.args.onnx_model)
        print("语音模型加载成功")

    def get_args(self):
        parser = argparse.ArgumentParser(description='inference')
        # 模型文件夹
        parser.add_argument('--onnx_model', default= self.mode_path)
        # 模型配置
        parser.add_argument('--cfg', default=self.config_path)
        args = parser.parse_args()
        return args

    def generated_speech(self,input_text,output_filename):
        text = f"[JA]{input_text}[JA]" if is_japanese(input_text) else f"[ZH]{input_text}[ZH]"
        # 将文本字符串转换为id
        seq = text_to_sequence(text, symbols=self.hyper_params.symbols,
                               cleaner_names=self.hyper_params.data.text_cleaners)
        if self.hyper_params.data.add_blank:
            seq = intersperse(seq, 0)
        with torch.no_grad():
            x = np.array([seq], dtype=np.int64)
            x_len = np.array([x.shape[1]], dtype=np.int64)
            sid = 0
            sid = np.array([sid], dtype=np.int64)
            scales = np.array([0.667, 0.8, 1], dtype=np.float32)
            scales.resize(1, 3)
            ort_inputs = {
                'input': x,
                'input_lengths': x_len,
                'scales': scales,
                'sid': sid
            }
            t1 = time.time()
            audio = np.squeeze(self.ort_session.run(None, ort_inputs))
            audio *= 32767.0 / max(0.01, np.max(np.abs(audio))) * 0.6
            audio = np.clip(audio, -32767.0, 32767.0)
            t2 = time.time()
            spending_time = "推理时间：" + str(t2 - t1) + "s"
            print(spending_time)

            wavfile.write('output/' + output_filename, self.hyper_params.data.sampling_rate,
                          audio.astype(np.int16))

    def playsound(self,path):
        playsound(path)