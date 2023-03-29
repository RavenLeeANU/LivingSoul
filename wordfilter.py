from pypinyin import lazy_pinyin
import os


class WordFilter:
    def __init__(self, config):
        self.sensitive_dict = []
        path = os.path.join(config["dict_path"], config["sensitive"])
        sensitive_file = open(path, 'r', encoding='utf-8')
        sensitive_raw = sensitive_file.readlines()

        self.py_sensitive_word = []
        for i in range(len(sensitive_raw)):
            sensitive_raw[i] = sensitive_raw[i].replace('\n', '')
            self.py_sensitive_word.append(str.join('', lazy_pinyin(sensitive_raw[i])))

    def filter_text(self, text):
        if text == '-1':
            return True
        text_py = str.join('', lazy_pinyin(text))
        for i in range(len(self.py_sensitive_word)):
            if self.py_sensitive_word[i] in text or self.py_sensitive_word[i] in text_py:
                return False
        return True
