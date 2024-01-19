# 关于她的聆音

语言：简体中文, [English](../Documentation.md)

这是一个配置她的听觉与话音的后端。你可以自行选择自己喜欢的后端，并为她配置独特的听觉与话音。

根据你选择的后端，对硬件的要求也就不同。反之，可以根据你的硬件选择合适的后端，只是满足通讯协议即可。

本项目基于[百度飞桨语音平台](https://github.com/PaddlePaddle/PaddleSpeech) 的开源项目，其前置安装条件请参考项目的说明。
不过，本项目也整理了基于开发时的硬件环境所使用的软件环境，仅供参考。

具体见 **_"[Documentation](../Documentation)"_** 文件夹。

# 安装

1. 先安装Python。
- 如果使用GPU，则安装CUDA基础环境。
2. 安装PaddlePaddle。
- 如果使用CPU，则按如下方法安装：
```commandline
python -m pip install paddlepaddle==2.4.2 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html -i https://pypi.tuna.tsinghua.edu.cn/simple
```
- 如果使用GPU，则安装[PaddlePaddle-GPU](#PaddlePaddle-GPU版本安装)。
3. 安装requirements.txt。
```commandline
python -m pip install -r requirements/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
4. 拷贝[nltk_data](../OTFiles/nltk_data)文件夹至所使用的Python环境根目录下。
5. 下载或自己训练的模型（包括文本转语音和语音识别），详见[PaddleSpeech Model List](https://github.com/PaddlePaddle/PaddleSpeech?tab=readme-ov-file#model-list) 。
6. 将下载的模型放置在server.py中指定的位置，或者修改代码为下载的位置。

## 依赖

- [Python](https://www.python.org/) (>=3.8，建议>=3.9)
- [PaddlePaddle](https://www.paddlepaddle.org.cn/) (<=2.5.1，建议=2.4.2)
- [PaddleSpeech](https://github.com/PaddlePaddle/PaddleSpeech/) (建议=[1.4.1](https://github.com/PaddlePaddle/PaddleSpeech/tree/r1.4.1))
- 其它依赖见"[requirements.txt](../requirements/requirements.txt)"。

## PaddlePaddle-GPU版本安装

**_在有多个Python环境时，注意Pip安装的位置是否为所在Python所使用的环境。_**

根据自己的显卡CUDA版本调整指令，比如版本是11.7，指令如下：
```commandline
python -m pip install paddlepaddle-gpu==2.4.2.post117 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html -i https://pypi.tuna.tsinghua.edu.cn/simple
```

# 使用

- 方式一：命令行定位到server.py所在目录，运行以下指令：

**（注意：多python环境时命令中的python应确保为刚刚配置的那个环境）**
```commandline
python server.py
```

- 方式二：运行[Launch](../Launch.bat)。

# 通讯协议

## 文本转语音

### 客户端请求数据

方式：Web Post

格式：json, UTF-8

内容：
```json lines
{
  // API 密钥
  "APIKey": "API001",
  // 话语文本
  "Word": "你好"
}
```

### 服务端返回数据

音频字节流。

## 语音转文本（语音识别）

### 客户端请求数据

方式：Web Post

格式：Web Form

内容：

|    键    |  格式  | 值   | 备注        |
|:-------:|:----:|-----|-----------|
| APIKey  |  文本  | --  | 值就自己自定义了  |
| file | 字节数组 | --  | 音频数据的字节数组 |

### 服务端返回数据

方式：Web Post

格式：json, UTF-8

内容：
```json lines
{
  // 转换（识别）后的结果
  "word": "你好"
}
```

## 重启指令

### 客户端请求数据

方式：Web Post

格式：json, UTF-8

内容：
```json lines
{
  // API 密钥
  "APIKey": "API001",
  // 指令名
  "cmd": "指令名"
}
```
目前支持指令名：

|    指令名    | 参数  | 功能   | 备注             |
|:-------:|:---:|------|----------------|
| restart  |  无  | 重启服务 |        |

### 服务端返回数据

方式：Web Post

格式：json, UTF-8, web

内容：

|    指令名    | 返回数据 | 功能   | 备注             |
|:-------:|:----:|------|----------------|
| restart  |  无   | 重启服务 |        |
异常返回数据：
- 返回响应状态码。
- 返回如下json数据表示异常原因：
```json lines
{
  "msg": "异常内容文本"
}
```

# 技术细节

## 已知限制

- 目前仅在Windows 10下做过测试，其它Python支持的平台理论上支持。

## 包体内容

以下表格展示了包中各主要文件夹或文件的功能：

| 位置                | 描述                      |
|--------------------|-------------------------|
| `..\server.py`          | 包含主要功能的业务代码。            |
| `..\Launch.bat`          | 包含命令行启动代码。              |
| `..\voice` | 包含语音模型文件，包括语音识别与文本转语音等。 |
| `..\APIKeys` | 包含API Key文件。            |
| `..\module` | 包含各种扩展模块。               |
| `..\requirements`  | 包含安装环境所需要的依赖模块。         |
| `..\OTFiles` | 包含其它未归类的文件，比如nltk_data。          |
| `..\Documentation` | 包含介绍与使用的多语言文档，比如主文档。    |

# 文档版本日志

| 日期         | 描述                     |
|------------|------------------------|
| 2024-01-19 | 文档（v1.0）创建，匹配包版本1.0.1。 |
