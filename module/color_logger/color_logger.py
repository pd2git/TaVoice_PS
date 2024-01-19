# ==========================================
# Copyright © AA. All rights reserved.
# Author：AA
# CreateTime：2023/12/06 11:35:30
# Version: v1.0
# Description：
# ==========================================

import logging
import colorlog

log_colors_config = {
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

color_logger = logging.getLogger('logger_name')

# 日志级别，logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
color_logger.setLevel(logging.DEBUG)

# 重复日志问题：
# 1、防止多次addHandler；
# 2、loggername 保证每次添加的时候不一样；
# 3、显示完log之后调用removeHandler
# if not logger.hasHandlers():
# 输出到控制台
console_handler = logging.StreamHandler()
# 日志级别，logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
console_handler.setLevel(logging.DEBUG)
# 日志输出格式
console_formatter = colorlog.ColoredFormatter(
    fmt='%(log_color)s[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] '
        ': %(message)s',
    datefmt='%Y-%m-%d  %H:%M:%S',
    log_colors=log_colors_config
)
console_handler.setFormatter(console_formatter)
#
if not color_logger.handlers:
    color_logger.addHandler(console_handler)

console_handler.close()

