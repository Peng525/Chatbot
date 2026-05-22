'''
This program requires the following modules:
- python-telegram-bot==22.5
- urllib3==2.6.2
'''
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
# 引入大模型对接模块（确保 ChatGPT_25.py 在同级目录下）
from ChatGPT_25 import ChatGPT
gpt = None
import configparser
import logging

def main():
    # 配置底层的日志输出格式与级别
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
        level=logging.INFO
    )
    
    # 初始化配置解析器并读取本地的 config.ini 配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # 【核心升级】在配置加载后、注册 Handler 之前，初始化大模型客户端对象
    global gpt
    gpt = ChatGPT(config)
    
    # 从配置中安全提取 Telegram Token 并构建 Application
    token = config['TELEGRAM']['ACCESS_TOKEN']
    app = ApplicationBuilder().token(token).build()
    
    # 注册消息处理器：过滤纯文本且排除斜杠命令
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, callback))
    
    # 启动机器人长轮询模式
    logging.info('初始化成功！')
    app.run_polling()


# 异步回调函数：处理接收到的所有纯文本消息
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await update.message.reply_text(response)
    logging.info("UPDATE: " + str(update))
    loading_message = await update.message.reply_text('思考中...')

    try:
        # 将用户发送的文本投递给大模型客户端进行处理
        response = gpt.submit(update.message.text)
        
        # 动态更新：大模型生成完毕后，利用其异步通道编辑并替换原有的 "思考中..." 文本
        await loading_message.edit_text(response)
        
    except Exception as e:
        # 异常容错处理
        logging.error(f"调用大模型发生错误: {e}")
        await loading_message.edit_text("大模型调用错误，请检查模型配置是否正确")

if __name__ == '__main__':
    
    main()
