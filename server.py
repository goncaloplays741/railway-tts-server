import io, json, os, tempfile, wave
from flask import Flask, request, send_file
import piper
import threading
app = Flask(__name__)
lock = threading.Lock()
cache = {}
def get_voice(lang):
    if lang not in cache:
        m = {
            'pt-BR':'pt_BR-faber-medium',
            'pt-PT':'pt_PT-tugão-medium',
            'en-US':'en_US-less-medium',
            'en-GB':'en_GB-alan-medium',
            'es-ES':'es_ES-sharvard-medium',
            'fr-FR':'fr_FR-siwis-medium',
            'de-DE':'de_DE-thorsten-medium',
            'it-IT':'it_IT-riccardo-medium',
            'ru-RU':'ru_RU-irina-medium',
            'zh-CN':'zh_CN-xiaohan-medium',
            'ja-JP':'ja_JP-kurenai-medium',
            'ko-KR':'ko_KR-jina-medium',
        }
        name = m.get(lang, 'en_US-less-medium')
        url = f'https://huggingface.co/rhasspy/piper-voices/resolve/main/{name}.onnx'
        cache[lang] = piper.load_voice(url)
    return cache[lang]
@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json(force=True)
    text = data.get('text','')[:500]
    lang = data.get('lang','en-US')
    if not text:
        return {'erro':'texto vazio'},400
    with lock:
        voz = get_voice(lang)
        buf = io.BytesIO()
        with wave.open(buf,'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(22050)
            for audio in piper.synthesize(text, voz):
                w.writeframes(audio)
        buf.seek(0)
    return send_file(buf, mimetype='audio/wav')
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)