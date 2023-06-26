import os
import re
import tempfile
import urllib

from bson import ObjectId
from qiniu import Auth, put_file

# 需要填写你的 Access Key 和 Secret Key
access_key = 'access_key'
secret_key = 'secret_key'
# 构建鉴权对象
q = Auth(access_key, secret_key)
# 要上传的空间
bucket_name = 'imgbed'

path = './zh-cn'

folders = []

uploaded = {}
for r, d, f in os.walk(path):
    for file in f:
        path = os.path.abspath(os.path.join(r, file))
        if path.endswith('.py') or path.endswith('.ipynb') or path.endswith(
                '.js') or path.endswith('.ts') or path.endswith(
            '.json') or path.endswith('.css') or path.endswith(
            '.less') or path.endswith('.md') or path.endswith('.markdown'):
            try:
                with open(path, 'r', encoding="utf-8", errors='ignore') as f:
                    content = f.read()
                    x = re.findall(
                        r'\!\[.*?\]\((https://cdn\.nlark\.com/yuque.*?)\)',
                        content)
                    imgs = x
                    if len(imgs) > 0:
                        print(path)
                        for img in imgs:
                            print('get:', img)
                            uploaded_url = uploaded.get(img)
                            if not uploaded_url:
                                key = ObjectId().__str__() + '.png'
                                token = q.upload_token(bucket_name, key)
                                with tempfile.TemporaryDirectory() as tmpdirname:
                                    localfile = os.path.join(tmpdirname, key)
                                    urllib.request.urlretrieve(img, localfile)
                                    ret, info = put_file(token, key, localfile)
                                    assert info.status_code == 200
                                uploaded_url = f'https://{bucket_name}.momodel.cn/{key}'
                                uploaded[img] = uploaded_url
                            content = content.replace(img, uploaded_url)
                            print('replace to: ', uploaded_url)
                        with open(path, 'w', encoding="utf-8",
                                  errors='ignore') as fw:
                            fw.write(content)
            except Exception as e:
                print('error path: ', path)
