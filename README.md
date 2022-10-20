# Paddleocr API

这是由 FastAPI 包装的 Paddleocr 文本识别接口，并使用 Pyinstaller 打包编译为可执行文件。

## 使用说明

- 适用于大部分 Windows 操作系统，其他系统暂未测试

  若提示缺少 DLL 异常请检查是否未启用【桌面体验】功能

- 启动参数

  --host 监听主机，默认：127.0.0.1

  --port 监听端口，默认：8000

  --lang 文本识别语言，默认：en

- 模型文件存放位置

  ~/.paddleocr
