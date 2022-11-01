# Paddleocr API

这是由 FastAPI 包装的 Paddleocr 文本识别 API 接口，并使用 Pyinstaller 打包编译为可执行文件。

## 使用说明

- 适用于大部分 Windows 操作系统，其他系统暂未测试

  若提示缺少 DLL 异常，请检查是否未启用【桌面体验】功能

- 启动参数

| 参数          | 注解       | 缺省           |
|-------------|----------|--------------|
| --host      | 监听主机     | 127.0.0.1    |
| --port      | 监听端口     | 8000         |
| --lang      | 文本识别语言   | en           |
| --model-dir | 模型文件存放位置 | ~\.paddleocr |

- 启动示例

```shell
.\PaddleocrAPI-v1.1.exe --lang=zh --model-dir=.\model
```

- 请求参数

| 参数  | 注解    | 缺省   |
|-----|-------|------|
| det | 识别    | True |
| rec | 检测    | True |
| cls | 方向分类器 | True |

- 请求示例

  - 基础变量

  ```python
  url = 'http://127.0.0.1:8000/ocr'
  image_binary = open('demo.png', 'rb').read()
  image_base64 = base64.b64encode(image_binary).decode()
  ```

  - 请求参数的使用

  ```python
  requests.post(
      url,
      params={'det': True, 'rec': True, 'cls': False},
      data=image_base64
  )
  ```

  - 在请求体中以文本形式 POST 一张 Base64 格式图片（推荐）

  ```python
  response = requests.post(url, data=image_base64)
  print(json.dumps(response.json()))
  ```

  - 在请求体中以 Form 表单形式 POST 一张或多张二进制图片

  ```python
  response = requests.post(url, files={'demo': image_binary})
  print(json.dumps(response.json()))
  ```

  - 在请求体中以 Form 表单形式 POST 一张或多张 Base64 格式图片

  ```python
  response = requests.post(url, data={'demo': image_base64})
  print(json.dumps(response.json()))
  ```

  - 在请求体中以 JSON 文本形式 POST 一张或多张 Base64 格式图片

  ```python
  response = requests.post(url, json={'demo': image_base64.decode()})
  print(json.dumps(response.json()))
  ```

## 编译说明

- 编译环境

  - 操作系统：Windows Server 2008 R2 x64

    注：需启用【桌面体验】功能

  - 软件版本：Python 3.8.10

    依赖参见 requirements.txt 文件

- 安装依赖

```shell
pip install -r requirements.txt
```

- 编译准备

  - 修改 image.py 文件，防止占用过高

  ```python
  # .\venv\site-packages\paddle\dataset\image.py
  
  if six.PY3:
      ...
      import_cv2_proc = subprocess.Popen(
          [interpreter, "-c", "import cv2"],
          stdin=subprocess.PIPE,  # <-- here
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE,
          shell=True)  # <-- here
      ...
  ```

- 执行编译

```shell
pyinstaller --clean main.spec
```
