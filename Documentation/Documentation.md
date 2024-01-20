# About her listening voice

Language：English, [简体中文](/Documentation_zh-CN.md)

This is a backend that configures her hearing and speech.
You can also choose your favorite backend and configure her unique hearing and voice.

Depending on the backend you choose, the hardware requirements will vary. On the contrary, you can choose the appropriate backend according to your hardware, as long as it meets the communication protocol.

This project is based on the open source project of [Baidu Paddle Speech Platform](https://github.com/PaddlePaddle/PaddleSpeech). Please refer to the project description for its pre-installation conditions.
However, this project also compiles the software environment used based on the hardware environment during development, for reference only.

See the **_"[Documentation](/Documentation)"_** folder for details.

# Installation

1. Install Python first.
- If using a GPU, install the CUDA base environment.
2. Install PaddlePaddle.
- If using CPU, install as follows:
```commandline
python -m pip install paddlepaddle==2.4.2 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html -i https://pypi.tuna.tsinghua.edu. cn/simple
```
- If using GPU, install [PaddlePaddle-GPU](#PaddlePaddle-GPU version installation).
3. Install requirements.txt.
```commandline
python -m pip install -r requirements/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
4. Copy the [nltk_data](/OTFiles/nltk_data) folder to the root directory of the Python environment used.
5. Download or train your own models (including text-to-speech and speech recognition), see [PaddleSpeech Model List](https://github.com/PaddlePaddle/PaddleSpeech?tab=readme-ov-file#model-list) for details .
6. Place the downloaded model at the location specified in server.py, or modify the code to the downloaded location.

## Dependencies

- [Python](https://www.python.org/) (>=3.8, recommended >=3.9)
- [PaddlePaddle](https://www.paddlepaddle.org.cn/) (<=2.5.1, recommended=2.4.2)
- [PaddleSpeech](https://github.com/PaddlePaddle/PaddleSpeech/) (Recommendation=[1.4.1](https://github.com/PaddlePaddle/PaddleSpeech/tree/r1.4.1))
- For other dependencies, see "[requirements.txt](/requirements/requirements.txt)".

## PaddlePaddle-GPU version installation

**_When there are multiple Python environments, pay attention to whether the location where Pip is installed is the environment used by Python._**

Adjust the instructions according to your own graphics card CUDA version. For example, if the version is 11.7, the instructions are as follows:
```commandline
python -m pip install paddlepaddle-gpu==2.4.2.post117 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html -i https://pypi.tuna. tsinghua.edu.cn/simple
```

# Usage

- Method 1: Navigate the command line to the directory where server.py is located and run the following command:

**(Note: When using multiple python environments, the python in the command should be the environment just configured)**
```commandline
python server.py
```

- Method 2: Run [Launch](/Launch.bat).

# Communication Protocol

## Text to Speech

### Client request data

Method: Web Post

Format: json, UTF-8

content:
```json lines
{
   // API key
   "APIKey": "API001",
   // Speech text
   "Word": "Hello"
}
```

### Server returns data

Audio byte stream.

## Speech to text (speech recognition)

### Client request data

Method: Web Post

Format: Web Form

Content:

| Key | Format | Value | Comments |
|:-------:|:----:|-----|-----------|
| APIKey | Text | -- | The value is customized |
| file | byte array | -- | byte array of audio data |

### Server returns data

Method: Web Post

Format: json, UTF-8

Content:
```json lines
{
   //The result after conversion (recognition)
   "word": "Hello"
}
```

## Restart command

### Client request data

Method: Web Post

Format: json, UTF-8

Content:
```json lines
{
   // API key
   "APIKey": "API001",
   // Command name
   "cmd": "command name"
}
```
Currently supported command names:

| Command name | Parameters | Function | Remarks |
|:-------:|:---:|------|----------------|
| restart | None | Restart service | |

### Server returns data

Method: Web Post

Format: json, UTF-8, web

Content:

| Command name | Return data | Function | Remarks |
|:-------:|:----:|------|----------------|
| restart | None | Restart service | |
Exception return data:
- Return response status code.
- The following json data is returned to indicate the cause of the exception:
```json lines
{
   "msg": "Exception content text"
}
```

# Technical details

## Known limitations

- Currently it has only been tested under Windows 10. It is theoretically supported on other platforms supported by Python.

## Package content

The following table shows the function of each major folder or file in the package:

| Location | Description |
|------------------------|-------------------------|
| `..\server.py` | Business code containing main functions. |
| `..\Launch.bat` | Contains command line startup code. |
| `..\voice` | Contains speech model files, including speech recognition and text-to-speech, etc. |
| `..\APIKeys` | Contains API Key files. |
| `..\module` | Contains various extension modules. |
| `..\requirements` | Contains dependent modules required for the installation environment. |
| `..\OTFiles` | Contains other uncategorized files, such as nltk_data. |
| `..\Documentation` | Multilingual documentation containing introduction and usage, such as the main document. |

# Document version log

| Date | Description |
|------------|------------------------|
| 2024-01-20 | The document (v1.0.1) is created to fix the file location.   |
| 2024-01-19 | Document (v1.0) created, matching package version 1.0.1. |
