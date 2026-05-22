import requests
import configparser
# ChatGPT REST API 的简单客户端
class ChatGPT:
    def __init__(self, config):
        # 从 ini 文件读取 API 配置值
        api_key = config['CHATGPT']['API_KEY']
        base_url = config['CHATGPT']['BASE_URL']
        model = config['CHATGPT']['MODEL']
        api_ver = config['CHATGPT']['API_VER']

        # 构建聊天自动补全的完整 REST 端点 URL
        self.url = f'{base_url}/deployments/{model}/chat/completions?api-version={api_ver}'

        # 设置身份验证和 JSON 负载所需的 HTTP 标头
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "api-key": api_key,
        }

        # 定义系统提示词以指导AI的输出风格
        self.system_message = (
            'You are a helper! Your users are university students. '
            'Your replies should be conversational, informative, use simple words, and be straightforward.'
        )

    def submit(self, user_message: str):
        
        # 构建对话历史：系统消息 + 用户消息
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_message},
        ]

        # 使用生成参数准备请求负载
        payload = {
            "messages": messages,
            "temperature": 1,     # 输出的随机性（越高越有创意）
            "max_tokens": 150,    # 回复的最大长度
            "top_p": 1,           # 核心采样参数
            "stream": False       # 禁用流式传输，等待完整回复
        }    

        # 向 ChatGPT REST 发送请求API
        response = requests.post(self.url, json=payload, headers=self.headers)

        # 如果成功，返回AI的回复文本
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            # 否则返回错误详情
            return "Error: " + response.text
    

if __name__ == '__main__':
    # 从 ini 文件加载配置
    config = configparser.ConfigParser()
    config.read('config.ini')    

    # 初始化 ChatGPT 客户端
    chatGPT = ChatGPT(config)

    # 简单的 REPL 循环：读取用户输入，发送到 ChatGPT，打印回复
    while True:
        print('Input your query: ', end='')
        response = chatGPT.submit(input())
        print(response)