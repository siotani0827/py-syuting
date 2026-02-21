#%reset -f
import os
import requests

# フォルダが存在しなければ作成
dir = 'data/download/'
if not os.path.isdir(dir):
  os.makedirs(dir)

fn = 'char-chip-01.png'
url = 'http://dispell.net/th/char_th0012.png'
res = requests.get(url)

if res.status_code != 200:
  raise Exception(f'ファイル {url} の取得に失敗。強制終了します。Code:{res.status_code}')
else :
  with open(f'{dir}/{fn}','wb') as file: 
    file.write(res.content)
  print(f'{dir} に {fn} を保存しました')