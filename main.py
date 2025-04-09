import os
import shutil
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import FastAPI, Request
import uvicorn
from pachka import Pachka
from chunks import Chunk
from dotenv import load_dotenv

app = FastAPI()
pachkaDef = Pachka()
chunk = Chunk(ch_size=1024)

source_directory = './new_files'
destination_directory = './RAG-Documents'

def move_files(src_dir, dest_dir):
    """Перемещает файлы из исходной директории в целевую."""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        dest_file = os.path.join(dest_dir, filename)

        if os.path.isfile(src_file):
            shutil.move(src_file, dest_file)
            print(f"Перемещен: {src_file} -> {dest_file}")

class WatcherHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            # Перемещение файла и обновление после перемещения
            print(f"Новый файл обнаружен: {event.src_path}")
            chunk.load_pdf(source_directory)  # Обновление после перемещения
            move_files(source_directory, destination_directory)

def start_watching():
    event_handler = WatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, path=source_directory, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

@app.post("/webhook")
async def webhook(request: Request):
    """Обрабатывает вебхуки и выполняет действия на основе входящих данных."""
    payload = await request.json()

    if str(payload.get('user_id')) != pachkaDef.USER_ID:
        if payload.get('content') == '/updatedb':
            move_files(source_directory, destination_directory)
            chunk.load_pdf(destination_directory)  # Обновление после перемещения
            
        chat_id = payload.get('chat_id')
        user_id = payload.get('user_id')
        if "@bot" in payload.get('content'):
            answer = await chunk.async_get_answer(query=payload.get('content').replace("/hello", "").replace("@bot", "").strip(),user_id=user_id)

            content = answer
            print(content)
            data_response = pachkaDef.send_response(user_id, chat_id, content)

        return {"status": "success"}

if __name__ == "__main__":
    # Запуск наблюдателя в отдельном потоке
    watcher_thread = threading.Thread(target=start_watching, daemon=True)
    watcher_thread.start()
    
    # Запуск FastAPI
    uvicorn.run(app, host="95.181.167.220", port=8000)