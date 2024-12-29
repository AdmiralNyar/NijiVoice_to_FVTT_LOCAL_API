# -*- coding: utf-8 -*-
import requests
import json
import logging
from logging import FileHandler
from datetime import datetime, timezone
from fastapi import FastAPI, Response, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel, root_validator
import PySimpleGUI as sg
import threading
from threading import Event, Lock, Thread
from contextlib import contextmanager
import time
import ctypes
import os
import keyring
import pygame
import io
import asyncio
import re
import socket
import colorama

colorama.init()
print('\033[31m' + 'にじボイスは株式会社Algomaticのサービスです。生成された音声はにじボイスの利用規約に基づく利用をしてください。' + '\033[0m')
print('\033[31m' + '特にコンテンツ公開の際のクレジット表記や禁止されているコンテンツでの利用については注意してください。' + '\033[0m')
print('\033[31m' + '本アプリはにじボイスのAPIを利用した非公式のアプリケーションです。本アプリの作成者はにじボイスの運営とは無関係です。' + '\033[0m')
print('\033[31m' + '本アプリについての問い合わせは、 https://github.com/AdmiralNyar/NijiVoice_to_FVTT_LOCAL_API までお願いします。' + '\033[0m')
print("")
print("")
print('\033[32m' + '#  #   #      #    #    #  #         #                       #                ####                       #            ' +'\033[0m')
print('\033[32m' + '## #                    #  #                                 #                #                          #            ' +'\033[0m')
print('\033[32m' + '## #  ##      #   ##    #  #   ##   ##     ##    ##         ###    ##         ###    ##   #  #  ###    ###  ###   #  #' +'\033[0m')
print('\033[32m' + '# ##   #      #    #    #  #  #  #   #    #     # ##         #    #  #        #     #  #  #  #  #  #  #  #  #  #  #  #' +'\033[0m')
print('\033[32m' + '# ##   #      #    #     ##   #  #   #    #     ##           #    #  #        #     #  #  #  #  #  #  #  #  #      # #' +'\033[0m')
print('\033[32m' + '#  #  ###   # #   ###    ##    ##   ###    ##    ##           ##   ##         #      ##    ###  #  #   ###  #       # ' +'\033[0m')
print('\033[32m' + '             #                                                                                                     #  ' +'\033[0m')
print("")
print("")
print('\033[31m' + '注意：アプリを終了するまでこのコマンド画面を閉じないでください' + '\033[0m')

def setup_logging():
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt="[%X]", handlers=[FileHandler(filename="log.txt")])
  return logging.getLogger("NijiVoice")

logger = setup_logging()

Kernel32 = ctypes.windll.Kernel32
mutex = Kernel32.CreateMutexA(0, 1, b"NijiVoiceConnectorRunning")
result = Kernel32.WaitForSingleObject(mutex, 0) 
if result in (0x80, 0x102):  # ERROR_TIMEOUT
    logger.error("Another process is already running. Exiting.")
elif result != 0:
    logger.error(f"Failed to create mutex: {ctypes.GetLastError()}")
    exit(1)

logger.info("Dual activation confirmation completed")

class Config:
  def __init__(self):
    try:
      self.type = keyring.get_password("NijiVoice", "type") or "mp3"
    except keyring.errors.KeyringError as e:
      logger.error(f"Error reading from keyring: {e}")
      self.type = "mp3"
    try:
      self.access_key = keyring.get_password("NijiVoice", "key") or ""
    except keyring.errors.KeyringError as e:
      logger.error(f"Error reading from keyring: {e}")
      self.access_key = ""
    try:
      self.folder_path = keyring.get_password("NijiVoice", "folder") or ""
    except keyring.errors.KeyringError as e:
      logger.error(f"Error reading from keyring: {e}")
      self.folder_path = ""
    try:
      fs = keyring.get_password("NijiVoice", "foldersetting")
      self.folder_setting = fs.lower() == "true"  if fs else False
    except keyring.errors.KeyringError as e:
      logger.error(f"Error reading from keyring: {e}")
      self.folder_setting =  "true"
    try:
      self.allow_origin = keyring.get_password("NijiVoice", "origin") or '["http://localhost:30000"]'
    except keyring.errors.KeyringError as e:
      logger.error(f"Error reading from keyring: {e}")
      self.allow_origin = '["http://localhost:30000"]'
  def save(self):
        keyring.set_password("NijiVoice", "type", self.type)
        keyring.set_password("NijiVoice", "key", self.access_key)
        keyring.set_password("NijiVoice", "folder", self.folder_path)
        keyring.set_password("NijiVoice", "foldersetting", str(self.folder_setting))
        keyring.set_password("NijiVoice", "origin", self.allow_origin)
  def reset(self):
        keyring.set_password("NijiVoice", "type", "mp3")
        keyring.set_password("NijiVoice", "key", "")
        keyring.set_password("NijiVoice", "folder", "")
        keyring.set_password("NijiVoice", "foldersetting", "true")
        keyring.set_password("NijiVoice", "origin", '["http://localhost:30000"]')

config = Config()

class Item(BaseModel):
  speaker: str
  text: str
  id: str
  volume: float | None = 0.5
  speed: float | None = 1.0

  @root_validator(pre=True)
  def check_format(cls, values):
      if not (0.0 <= values.get('volume', 0.5) <= 1.0):
          raise ValueError("Volume must be between 0.0 and 1.0")
      if not (0.4 <= values.get('speed', 1.0) <= 3.0):
          raise ValueError("Volume must be between 0.4 and 3.0")
      return values

class UserOut(BaseModel):
  response: object
  status: str

# FastAPI App
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins= [*json.loads(config.allow_origin)],
    allow_methods=['POST', 'OPTIONS'],
    allow_headers=["Content-Type", "Authorization", "x-api-key"]
)

# Thread-safe Lock
file_lock = Lock()

@contextmanager
def pygame_mixer():
  try:
    pygame.mixer.init()
    yield
  except pygame.error as e:
    logger.error(f"Pygame initialization error: {e}")
  finally:
    pygame.mixer.quit()

def fetch_with_retries(url, retries=3, delay=1):
  for attempt in range(retries):
      try:
          response = requests.get(url, stream=True, timeout=10)
          response.raise_for_status()
          return response
      except requests.exceptions.RequestException as e:
          logger.warning(f"Retry {attempt + 1} failed: {e}")
          time.sleep(delay)
  raise ValueError("Maximum retry attempts exceeded.")

# 再生待ちのキューを作成 
audio_queue = asyncio.Queue()

async def play_audio(url: str, volume: float = 0.5):
  try:
      await audio_queue.put((url, volume))
  except asyncio.QueueFull:
      logger.error("Queue is full, audio task could not be added.")

async def audio_player():
  with pygame_mixer():
    while not shutdown_event.is_set():
      try:
        url, volume = await asyncio.wait_for(audio_queue.get(), timeout=1.0)
        try:
          # 音声データを取得
          response = requests.get(url, stream=True, timeout=10)
          response.raise_for_status()
          audio_data = io.BytesIO(response.content)
          
          # 音声データをロード
          pygame.mixer.music.load(audio_data)
          
          # 音量を設定
          pygame.mixer.music.set_volume(volume)
          
          # 音声を再生
          pygame.mixer.music.play()
          
          # 再生終了まで待機
          while pygame.mixer.music.get_busy():
              await asyncio.sleep(0.1)
        except requests.exceptions.RequestException as e: 
          logger.error(f"Error fetching audio: {e}") 
        except pygame.error as e: 
          logger.error(f"Error playing audio: {e}")
        finally: 
          audio_queue.task_done()
      except asyncio.TimeoutError:
        continue

# 終了時にキューを空にする処理
@app.on_event("shutdown")
async def shutdown_event_handler():
    logger.info("Shutting down...")
    while not audio_queue.empty():
      try:
        _= await audio_queue.get()
        audio_queue.task_done()
      except asyncio.QueueEmpty:
        break
      except Exception as e:
        logger.error(f"Error while processing shutdown queue: {e}")
    shutdown_event.set()
    logger.info("All queued tasks have been processed.")

# FastAPIの起動時にaudio_playerタスクを開始 
@app.on_event("startup") 
async def startup_event(): 
  logger.info("Start up sudio player...")
  asyncio.create_task(audio_player())


def save_audio(url, file_type, speaker, first_20_chars):
  with file_lock:
    try:
      logger.info("RECEIVE URL:" + url)
      dt = datetime.now()
      file_name = f"{dt.strftime('%Y%m%d%H%M%S')}_{first_20_chars}_{speaker}.{file_type}"
      folder_path = config.folder_path
      path = os.path.abspath(folder_path)
      if not os.path.isdir(folder_path):
        raise ValueError(f"Invalid folder path: {folder_path}")
      os.makedirs(path, exist_ok=True)
      re = fetch_with_retries(url)
      file_path = os.path.join(path, file_name)
      with open(file_path, 'wb') as f:
        for chunk in re.iter_content(chunk_size=1024):
          if chunk:
            f.write(chunk)
      logger.info(f"File saved: {file_path}")
    except Exception as e:
            logger.error(f"Error saving audio: {e}")

def call_nijivoice_api(id, payload):
    url = f'https://api.nijivoice.com/api/platform/v1/voice-actors/{id}/generate-voice'
    masked_key = f"{config.access_key[:3]}{'*' * (len(config.access_key) - 6)}{config.access_key[-3:]}"  # マスク処理
    session = requests.Session()
    try:
        response = session.post(url, json=payload, headers={
            'Content-Type': 'application/json',
            'x-api-key': config.access_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"API call error with masked key ({masked_key}): {e}")
        return None
    finally:
        session.close()  # セッションを明示的に終了
        logger.info("Session closed successfully")

@app.get("/getList", response_model = UserOut, status_code=status.HTTP_200_OK)
def getlist(request: Request):
  logger.info("Get the NijiVoice List")
  logger.info(f"Origin:{request.headers.get('origin')}")
  url = "https://api.nijivoice.com/api/platform/v1/voice-actors"
  masked_key = f"{config.access_key[:3]}{'*' * (len(config.access_key) - 6)}{config.access_key[-3:]}"  # マスク処理
  session = requests.Session()
  try:
    response = session.get(url, headers={
      'Content-Type': 'application/json',
      "accept": "application/json",
      "x-api-key": config.access_key,
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }, timeout=10)
    response.raise_for_status()
    return {"response": response.json(), "status": status.HTTP_200_OK}
  except requests.exceptions.RequestException as e:
    logger.error(f"API call error with masked key ({masked_key}): {e}")
    return {"response": "", "status": status.HTTP_502_BAD_GATEWAY}
  finally:
    session.close()  # セッションを明示的に終了
    logger.info("Session closed successfully")

@app.post("/getVoice", response_model = UserOut, status_code=status.HTTP_200_OK)
async def req(item: Item, res: Response, request: Request, background_tasks: BackgroundTasks):
    if request.headers['content-type'] == 'application/json':
        logger.info("Get the NijiVoice")
        text = item.text
        id = item.id
        speed = item.speed
        format = config.type
        volume = item.volume
        speaker = item.speaker
        first_20_chars = text[:20]
        payload = {
            "format": format,
            "script": text,
            "speed": str(speed)
        }
        response = call_nijivoice_api(id, payload)
        if not response:
           res.status_code = status.HTTP_502_BAD_GATEWAY
           return {"response": "", "status": status.HTTP_502_BAD_GATEWAY}

        try:
          response_json = response.json()
          if response.status_code == 200 and 'generatedVoice' in response_json:
            generate = response_json['generatedVoice']
            url= generate['audioFileDownloadUrl']
            if config.folder_setting == True:
              background_tasks.add_task(save_audio, url, format, speaker, first_20_chars)
            await play_audio(url = generate['audioFileUrl'], volume = volume)
            return {"response": response_json, "status": response.status_code}
        except json.JSONDecodeError as e:
          logger.error(f"Invalid JSON response: {e}")
          res.status_code = status.HTTP_502_BAD_GATEWAY
          return {"response": "", "status": status.HTTP_502_BAD_GATEWAY}
    res.status_code = status.HTTP_400_BAD_REQUEST
    return {"response": "", "status": status.HTTP_400_BAD_REQUEST}

def server_launch(port):
  global shutdown_event

  async def stop_server():
    shutdown_event.set()  # 停止フラグを設定
    logger.info("This server is shut down...")

  if __name__ == "__main__":
    global result
    if result != 0:
      logger.error("Another process is already running")
    else:
      try:
        logger.info("This server is up and running...")
        uvicorn.run(app, host='localhost', port=port)
      except Exception as e:
        logger.error(f"An error occurred while starting this server: {e}")
      finally:
        asyncio.run(stop_server())

def gui_lunch(key, path, setting, origin, file_type):
    logger.info("Launching GUI...")
    sg.theme('GrayGrayGray')

    column1 = [
      [sg.FolderBrowse("DL先フォルダ", font=("", 10)), sg.InputText(default_text=path,font=("", 10), key="-folderpath-")]
    ]

    column2 = [
      [sg.Button('サーバーを立ち上げる', font=("", 10), key="-btn-", p=((0,10),(0,0))), sg.Button('終了する', font=("", 10),key='-exit-',p=((10,0),(0,0))), sg.Button('設定をリセットする', font=("", 10), key="-reset-",p=((10,0),(0,0)))]
    ]

    frame2 = [[
            sg.Column(column1), sg.VPush()
          ],
          [
            sg.Column([[sg.Text('DLデータの拡張子を選択してください', size=(None, 1), font=("", 10)), sg.Combo(('mp3', 'wav'), default_value=file_type, readonly=True, key="-type-", font=("", 10))]], vertical_alignment="center")
          ]]

    frame = sg.Frame('',
        [
          [
            sg.Text('❶NijiVoice APIのアクセスキーを入力してください', size=(None, 2), font=("", 10))
          ],
          [
            sg.Input(default_text=key, key='-accesskey-', readonly=False, disabled=False, use_readonly_for_disable=False, password_char="*")
          ],
          [
            sg.Checkbox("パスワードを表示する", enable_events=True, key="-toggle_password-")
          ],
          [
            sg.Text('❷起動するポート番号を入力してください', size=(None, 1), font=("", 10))
          ],
          [
            sg.Input(default_text="2000", key='-port-', size=(10, 1))
          ],
          [
            sg.Text('❸APIにアクセス許可するサーバーアドレスを入力してください', size=(None, 1), font=("", 10))
          ],
          [
            sg.Input(default_text=json.loads(origin)[0], key='-origin-')
            ],
          [
            sg.Checkbox("音声ファイルをダウンロードする", font=("", 10), default=setting, key="-dlsetting-", change_submits=True)
          ],
          [
            sg.Frame(title="", layout=frame2, relief=sg.RELIEF_SUNKEN, key="-activatedl-", visible=setting)
          ]

        ] , size=(350, 300), key="-frame-"
    )

    layout = [
              [frame],
              [sg.Column(column2, element_justification="center")]
    ]

    window = sg.Window('NijiVoice to Foundry', layout, icon="nvl.ico")

    global shutdown_event

    while not shutdown_event.is_set():  # Event Loop
      try:
        event, value = window.read(timeout=500,timeout_key='-timeout-')

        if event in (sg.WIN_CLOSED, '-exit-'):
            value = sg.popup_ok_cancel('ソフト自体を終了させる場合はOKを、\n設定画面を再表示させる場合はキャンセルを押してください', title="終了の確認")
            if value == "OK":
              shutdown_event.set()
              break
        if event == "-btn-":
            logger.info("Starting server startup process...")
            config.type = value["-type-"]
            config.access_key = value['-accesskey-']
            config.folder_setting = value["-dlsetting-"]
            if config.folder_setting:
              config.folder_path = value["-folderpath-"]
            else:
              config.folder_path = ""

            origin = validate_and_clean_origin(value["-origin-"])
            if origin:
              config.allow_origin = origin
            else:
              sg.popup_error(f"以下のオリジンが無効です:\n{origin}")
              continue

            try:
               port = int(value['-port-'])
               if not (1 <= port <= 65535):
                  raise ValueError("ポート番号は1から65535の間で指定してください。")
            except ValueError as e:
               sg.popup_error(f"ポート番号が無効です: {e}")
               continue
            
            config.save()  
            window.close()
            server_launch(port)

        if event == "-dlsetting-":
                window["-activatedl-"].update(visible=value["-dlsetting-"])
        if event == "-toggle_password-":
          if value["-toggle_password-"]:
            window["-accesskey-"].update(password_char="")
          else:
            window["-accesskey-"].update(password_char="*")
        if event == "-reset-":
            confirm = sg.popup_yes_no("入力内容をデフォルト値にリセットしますか？")
            if confirm == "Yes":
              config.type = "mp3"
              config.access_key = ""
              config.folder_path = ""
              config.folder_setting = "true"
              config.allow_origin = '["http://localhost:30000"]'
              window["-type-"].update('mp3')
              window["-accesskey-"].update('')
              window["-folderpath-"].update('')
              window["-dlsetting-"].update(value=True)
              window["-activatedl-"].update(visible=True)
              window["-origin-"].update('http://localhost:30000')
              config.reset()
      except KeyboardInterrupt:
        break
      except ValueError as ve:
                sg.popup_error(f"Error: {ve}")
      except Exception as e:
         sg.popup_error(f"Unexpected error: {e}")
         break

    window.close()

def get_local_ip():
   try:
      hostname = socket.gethostname()
      return socket.gethostbyname(hostname)
   except socket.error as e:
      logger.error(f"Failed to get local IP: {e}")
      return None

def validate_and_clean_origin(origin):
  origin = origin.strip()
  origin_extraction_pattern = re.compile(
        r"^(https?):\/\/"  # プロトコル
        r"((([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})|localhost|(?:\d{1,3}\.){3}\d{1,3})" # ドメイン名、localhost、またはIPアドレス
        r"(:\d+)?"  # オプションのポート番号
        r"(\/.*)?$" # パス部分（オプション）
    )
  match = origin_extraction_pattern.match(origin)
  if match:
    protocol, host, port = match.group(1), match.group(2), match.group(5) or ""
    cleaned_origin = f"{protocol}://{host}{port}"
    adress = [cleaned_origin]
    local_ip = get_local_ip()
    if local_ip and (host == "localhost" or host == local_ip):
       adress.append(f"{protocol}://127.0.0.1{port}")
       adress.append(f"{protocol}://localhost{port}")
    logger.info(f"Setting allow-origin: {adress}")
    return json.dumps(adress)
  else:
    logger.error(f"Failed to set the allow-origin: {origin}")
    return None



shutdown_event = Event()

def main():
  global shutdown_event
  while not shutdown_event.is_set():
    time.sleep(1)

if result == 0:
  thread = threading.Thread(target=main, daemon=False)
  thread.start()

  while not shutdown_event.is_set():
    try:
      gui_lunch(key=config.access_key, path=config.folder_path,setting=config.folder_setting, origin=config.allow_origin, file_type=config.type)
    except Exception as e:
          sg.popup_error(f"Unexpected error: {e}")
    finally:
      shutdown_event.set()
      thread.join()
else:
  logger.error("Another process is already running")