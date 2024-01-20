# ==========================================
# Copyright © AA. All rights reserved.
# Author：AA
# CreateTime：2023/04/22 18:19:30
# Version: v1.0.1
# Description：
# 主功能模块，包含语音转文本，语音识别及指令控制三个模块。
# The main functional module includes three modules: voice to text conversion, speech recognition, and instruction control.
# ==========================================

import functools
import json
import logging
import ssl
import sys
import os
import time
import bottle
import uvicorn

from module.color_logger.color_logger import color_logger
from paddlespeech.cli.tts import TTSExecutor
from bottle import route, request, response
from module.options import cmd_opts
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from paddlespeech.cli.asr import ASRExecutor
from paddlespeech.cli.text import TextExecutor
# 控制台文本带颜色
# Console text with color
from colorama import init, Fore, Style

# 初始化 colorama 库，以在 Windows 终端中启用 ANSI 转义序列
# Initialize the colorama library to enable ANSI escape sequences in Windows terminalsinit()

# 全局属性
# 是否开启调试
# 注意开启调试的地方启用或禁用了哪些功能
# Global properties
# Whether to enable debugging
# Pay attention to which functions are enabled or disabled where debugging is enabled
is_debug = False

app = FastAPI(title="XyVoice",
              description="XyVoice API",
              version="1.0.1",
              openapi_url="/api/v1/openapi.json",
              docs_url="/api/v1/docs",
              redoc_url="/api/v1/redoc")

# 创建临时目录
# Create temporary directory
tem_voice_dir = "./temp/voice/"
if not os.path.exists(tem_voice_dir):
    os.makedirs(tem_voice_dir)


# 从配置文件加载数据
# Load data from configuration file
def load_line_txt_data(file_name):
    with open(f"./APIKeys/{file_name}.txt", "r") as f:
        return f.readlines()


# 检查API key
# Check API key
def check_api_key(api_key: str, api_keys_list):
    error = None
    if api_key is None:
        error = "The input api_key is empty."
    else:
        if api_key not in api_keys_list:
            error = "The input api_key is invalid."

    if error is not None:
        # 412=Precondition Failed	客户端请求信息的先决条件错误
        # 412=Precondition Failed	Wrong prerequisite for client requesting information
        return log_response_msg(error, 412, logging.WARN)
    else:
        return None


# 输出彩色日志至控制台，并响应
# Output colored logs to the console and respond
def log_response_msg(msg, status, log_level):
    match log_level:
        case logging.DEBUG:
            color_logger.debug(msg)
        case logging.INFO:
            color_logger.info(msg)
        case logging.WARNING | logging.WARN:
            color_logger.warning(msg)
        case logging.ERROR:
            color_logger.error(msg)
        case logging.CRITICAL:
            color_logger.critical(msg)
    #
    msg_data = {
        "msg": msg,
    }
    response.status = status
    response.content_type = "application/json"
    response.body = json.dumps(msg_data)
    return response


# region TTS
# 使用gpu 或 cpu计算
# Compute using gpu or cpu
tts_device = "cpu"

# 临时文件
# Temporary Files
tts_temp_file = f"{tem_voice_dir}tts_temp.wav"

# 加载TTS
tts_executor = None


def load_tts_service():
    global tts_executor
    tts_executor = TTSExecutor()


# 加载TTS Tokens
tts_api_keys = load_line_txt_data('TTS_APIKeys')


@route('/tts', method=('POST', "OPTIONS"))
def tts_service():
    # 计时开始
    # Timing begins
    start_time = time.time()
    # 接收文本
    # receive text
    rev_json = request.json
    # 校验API Key
    # Verify API key
    if rev_json is not None:
        rs = check_api_key(rev_json.get("APIKey"), tts_api_keys)
        if rs is not None:
            color_logger.warning(response.body)
            return rs
        else:
            text = rev_json.get("Word")
    else:
        return log_response_msg("Can not get the json data from the request.", 400, logging.WARN)

    color_logger.info(f"{Fore.BLUE}[TTS][Input]:{Style.RESET_ALL}{text}")

    if text is None or len(text) == 0:
        # 412=Precondition Failed	客户端请求信息的先决条件错误
        # 412=Precondition Failed	Wrong prerequisite for client requesting information
        return log_response_msg("The input text is empty", 412, logging.WARN)

    # 音频产生
    # Audio generation
    tts_executor(
        text=text,
        output=tts_temp_file,
        am='fastspeech2_mix',
        am_ckpt='./voice/Inner/fastspeech2_mix.onnx',
        phones_dict='./voice/Inner/phone_id_map.txt',
        speaker_dict='./voice/Inner/speaker_id_map.txt',
        voc='pwgan_aishell3',
        voc_ckpt='./pwgan/Inner/pwgan_aishell3.onnx',
        lang='zh',
        device=tts_device,
        # 转换成ONNX并使用CPU全部24个逻辑核心跑
        # Convert to ONNX and run using all 24 logical cores of the CPU.
        use_onnx=True,
        # 自动分配线程
        # 请注意：
        # 1.在将cpu_threads参数设置为大于1的值时，您的计算机可能会使用更多的CPU资源，因此您可能需要确保您有足够的资源来支持所需的线程数。
        # 2.但对于较小的模型，适当地减少线程数量可能会降低执行时间。
        # Automatically allocate threads
        # Please note:
        # 1. When setting the cpu_threads parameter to a value greater than 1, your computer may use more CPU resources, so you may need to ensure that you have enough resources to support the required number of threads.
        # 2. But for smaller models, appropriately reducing the number of threads may reduce the execution time.
        cpu_threads=-1)

    # 计时结束
    # End of timer
    end_time = time.time()
    execution_time = end_time - start_time
    color_logger.info(f"[TTS][Output]({execution_time:.5f}sec):(Audio) ")
    # 响应body中写入音频数据
    # Write audio data in the response body
    with open(tts_temp_file, "rb") as f:
        yield f.read()
    return response


# endregion

# region ARS
# 语音识别
# Speech recognition
asr_executor = ASRExecutor()

# 使用gpu 或 cpu计算
# Calculate using GPU or CPU
asr_device = "cpu"

# 预先加载模型
# Preload model
asr_model_type = 'conformer_wenetspeech'
asr_cfg_path = './Models/Inner/paddlespeech/models/conformer_wenetspeech-zh-16k/1.0/asr1_conformer_wenetspeech_ckpt_0.1.1' \
               '.model.tar/model.yaml'
asr_ckpt_path = './Models/Inner/paddlespeech/models/conformer_wenetspeech-zh-16k/1.0/asr1_conformer_wenetspeech_ckpt_0.1.1' \
                '.model.tar/exp/conformer/checkpoints/wenetspeech'


def load_asr_service():
    asr_executor._init_from_path(
        model_type=asr_model_type,
        cfg_path=asr_cfg_path,
        ckpt_path=asr_ckpt_path
    )


# 标点恢复
# Punctuation recovery
text_pun_executor = TextExecutor()

# 预先加载模型
# Preload model
tpr_config = './Models/Inner/paddlespeech/models/ernie_linear_p7_wudao-punc-zh/1.0/ernie_linear_p7_wudao-punc-zh.tar/ckpt' \
             '/model_config.json'
tpr_ckpt_path = './Models/Inner/paddlespeech/models/ernie_linear_p7_wudao-punc-zh/1.0/ernie_linear_p7_wudao-punc-zh.tar' \
                '/ckpt/model_state.pdparams'
tpr_punc_vocab = './Models/Inner/paddlespeech/models/ernie_linear_p7_wudao-punc-zh/1.0/ernie_linear_p7_wudao-punc-zh.tar' \
                 '/punc_vocab.txt'


def load_pun_service():
    text_pun_executor._init_from_path(
        cfg_path=tpr_config,
        ckpt_path=tpr_ckpt_path,
        vocab_file=tpr_punc_vocab
    )


# 临时文件
# Temporary files
asr_temp_file = f"{tem_voice_dir}asr_temp.wav"

# 加载TTS Tokens
# Load TTS Tokens
asr_api_keys = load_line_txt_data('ASR_APIKeys')


@route('/asr', method=('POST', "OPTIONS"))
def ars_service():
    # 计时开始
    # Start timing
    start_time = time.time()
    # 校验API Key
    # Verify API Key
    api_key = request.forms.get('APIKey')
    if api_key is not None:
        rs = check_api_key(api_key, asr_api_keys)
        if rs is not None:
            color_logger.warning(response.body)
            return rs
    else:
        # 412=Precondition Failed	客户端请求信息的先决条件错误
        # 412=Precondition Failed	The prerequisite for client request information is incorrect
        return log_response_msg("Can not get API key. Please pass with API key.", 412, logging.WARN)

    # 读取音频文件
    # Reading audio files
    uploaded_file = request.files['file']
    color_logger.info(f"{Fore.BLUE}[ARS][Input]:{Style.RESET_ALL}(Audio)")
    if uploaded_file is None:
        # 412=Precondition Failed	客户端请求信息的先决条件错误
        # 412=Precondition Failed	The prerequisite for client request information is incorrect
        return log_response_msg("The input audio file is null.", 412, logging.WARN)
    # 存储音频数据到临时文件
    # Store audio data to temporary files
    uploaded_file.save(asr_temp_file, overwrite=True)
    # 语音识别
    text = asr_executor(
        model=asr_model_type,
        config=asr_cfg_path,
        ckpt_path=asr_ckpt_path,
        audio_file=asr_temp_file,
        device=asr_device)
    # 计时结束
    # Stop timing
    end_time = time.time()
    execution_time = end_time - start_time
    color_logger.info(f"[ASR][Output] ({execution_time:.5f}sec):{text}")
    # 标点恢复
    # Punctuation recovery
    # 计时开始
    # Start timing
    start_time = time.time()
    text = text_pun_executor(text=text,
                             config=tpr_config,
                             ckpt_path=tpr_ckpt_path,
                             punc_vocab=tpr_punc_vocab,
                             device=asr_device
                             )
    # 计时结束
    # Stop timing
    end_time = time.time()
    execution_time = end_time - start_time
    color_logger.info(f"[Pun][Output]({execution_time:.5f}sec):{text}")
    # 返回数据
    # reply data
    response.content_type = "application/json;charset=utf-8"
    response.body = json.dumps({'word': text})
    return response


# endregion

# region Command

@route('/cmd', method=('POST', "OPTIONS"))
def cmd_service():
    # 接收文本
    # receive text
    rev_json = request.json
    # 校验API Key
    # Verify API key
    if rev_json is not None:
        rs = check_api_key(rev_json.get("APIKey"), tts_api_keys + asr_api_keys)
        if rs is not None:
            color_logger.warning(response.body)
            return rs
        else:
            cmd = rev_json.get("cmd")
    else:
        return log_response_msg("Can not get the json data from the request.", 400, logging.WARN)
    # 解析数据
    # Parsing data
    if cmd is None or cmd == '':
        # 412=Precondition Failed	客户端请求信息的先决条件错误
        # 412=Precondition Failed	The prerequisite for client request information is incorrect
        return log_response_msg('The command is none.', 412, logging.WARN)
    if cmd == 'restart':
        color_logger.warn("Restarting...")
        server.force_exit = True
        sys.exit()
    else:
        return log_response_msg(f"The command '{cmd}' is not supported.", 404, logging.WARN)


# endregion

def pathinfo_adjust_wrapper(func):
    # A wrapper for _handle() method
    @functools.wraps(func)
    def _(s, environ):
        environ["PATH_INFO"] = environ["PATH_INFO"].encode(
            "utf8").decode("latin1")
        return func(s, environ)

    return _

# 修复bottle在处理utf8 url时的bug
# Fix bottle's bug when processing utf8 url
bottle.Bottle._handle = pathinfo_adjust_wrapper(
    bottle.Bottle._handle)

app.mount(path="/api/", app=WSGIMiddleware(bottle.app[0]))

# uvicorn server
server = uvicorn.Server(uvicorn.Config(app))

if __name__ == "__main__":
    # 加载资源
    # Load resources
    if not is_debug:
        load_tts_service()
        load_asr_service()
        load_pun_service()
    # 有自签名文件就使用https。
    # If you have a self-signed file, use https.
    # [版本管理忽略数据-开始]
    # [Version Management Ignore Data-Start]
    ssl_root_path = f'{os.getcwd()}/../Safe/SSL/'
    ssl_key_file = f'{ssl_root_path}/key.pem'
    ssl_cert_file = f'{ssl_root_path}/cert.pem'
    # [版本管理忽略数据-结束]
    # [Version Management Ignore Data-End]
    host = "0.0.0.0"
    address = f"{host}:{cmd_opts.port}"
    if os.path.exists(ssl_key_file) and os.path.exists(ssl_cert_file):
        print("\033[0;32;32mFound the ssl config files and will use https.\033[0m")
        uvicorn.run(app, host=host, port=cmd_opts.port,
                    ssl_keyfile=ssl_key_file,
                    ssl_certfile=ssl_cert_file,
                    ssl_cert_reqs=ssl.CERT_NONE,
                    # ssl_ca_certs=ssl_ca_cert_file,
                    log_level='error',
                    loop="asyncio")
        address = f"https://{address}"
    # 否则使用http。
    # Otherwise use http.
    else:
        print("Can not find the ssl config files and will use http.")
        uvicorn.run(app, host=host, port=cmd_opts.port,
                    log_level='error', loop="asyncio")
        address = f"http://{address}"
    color_logger.info(f"Server is on at {address}.")
