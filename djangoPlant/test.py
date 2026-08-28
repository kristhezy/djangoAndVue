# # 定义颜色常量
# RED = '\033[91m'
# GREEN = '\033[92m'
# YELLOW = '\033[93m'
# BLUE = '\033[94m'
# RESET = '\033[0m'  # 重置颜色
# BOLD = '\033[1m'

# import urllib.request
# import tempfile
# import os
# import ssl
# from mutagen.mp3 import MP3

# def get_audio_info(url):
#     """获取音频时长（毫秒）和帧率"""
#     # macOS Python 默认不信任系统证书，跳过 SSL 验证
#     ctx = ssl.create_default_context()
#     ctx.check_hostname = False
#     ctx.verify_mode = ssl.CERT_NONE
#     with urllib.request.urlopen(url, timeout=30, context=ctx) as resp:
#         tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
#         tmp.write(resp.read())
#         tmp.close()

#     try:
#         audio = MP3(tmp.name)
#         duration_sec = audio.info.length
#         duration_ms = round(duration_sec * 1000, 3)
#         sample_rate = audio.info.sample_rate
#         bitrate = audio.info.bitrate
#         channels = audio.info.channels
#         layer = audio.info.layer
#         mpeg_version = audio.info.version
#         # MP3 帧率 = 采样率 / 每帧采样数
#         # Layer 3: MPEG-1 为 1152, MPEG-2/2.5 为 576
#         if mpeg_version == 1.0:
#             samples_per_frame = 1152
#         else:
#             samples_per_frame = 576
#         frames_per_sec = round(sample_rate / samples_per_frame, 4)

#         print(f"时长: {duration_sec} 秒")
#         print(f"时长: {duration_ms} 毫秒")
#         print(f"MP3 帧率: {frames_per_sec} 帧/秒")
#         print(f"  - 采样率: {sample_rate} Hz")
#         print(f"  - samples_per_frame: {samples_per_frame} (MPEG {'1.0' if mpeg_version == 1.0 else '2.x'})")
#         print(f"比特率: {bitrate} bps")
#         print(f"声道数: {channels}")
#         print(f"MP3 Layer: {layer}")
#     finally:
#         os.unlink(tmp.name)

# # if __name__ == '__main__':
# #     url = "https://file.mmeett.com/image/flutter/2053750606494011392.mp3"
# #     get_audio_info(url)


