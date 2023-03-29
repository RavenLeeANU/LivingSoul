import openai
import os
from wordfilter import WordFilter

class ChatBot:
    def __init__(self, config):
        self.filter = WordFilter(config=config)
        path = os.path.join(config["dict_path"], config["role_file"])
        sensitive_file = open(path, 'r', encoding='utf-8')

        role_description = sensitive_file.read()
        self.role_info = [{"role": "system", "content": role_description}]

        openai.api_key = config["secret_key"]
        openai.api_base = config["api_base"]
        self.model_name = config["gpt_model"]

    def chat(self, message):
        response = openai.ChatCompletion.create(model=self.model_name, messages=message)
        response_content = str(response['choices'][0]['message']['content'])

        # 敏感词词音过滤
        if not self.filter.filter_text(response_content):
            print("检测到敏感词内容::" + response_content)
            return "不懂你在说什么"

        print("从gpt接收::" + response_content)

        return response_content

