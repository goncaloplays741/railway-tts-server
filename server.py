import os, tempfile, uuid, datetime
from flask import Flask, request, send_file
import requests
app = Flask(__name__)
VOZES = {
  'pt-BR':'pt-BR-FranciscaNeural','pt-PT':'pt-PT-RaquelNeural',
  'en-US':'en-US-JennyNeural','en-GB':'en-GB-LibbyNeural',
  'es-ES':'es-ES-ElviraNeural','es-MX':'es-MX-DaliaNeural',
  'fr-FR':'fr-FR-DeniseNeural','de-DE':'de-DE-KatjaNeural',
  'it-IT':'it-IT-ElsaNeural','ja-JP':'ja-JP-NanamiNeural',
  'ko-KR':'ko-KR-SunHiNeural','zh-CN':'zh-CN-XiaoxiaoNeural',
  'ru-RU':'ru-RU-SvetlanaNeural','hi-IN':'hi-IN-SwaraNeural',
  'ar-SA':'ar-SA-ZariyahNeural','nl-NL':'nl-NL-ColetteNeural',
  'tr-TR':'tr-TR-EmelNeural','pl-PL':'pl-PL-AgnieszkaNeural',
}
def escapar(texto):
  return texto.replace('&','&').replace('<','<').replace('>','>').replace('"','"').replace("'",''')
@app.route('/tts', methods=['POST'])
def tts():
  try:
    dados = request.get_json(force=True)
    texto = dados.get('text','')[:500]
    lang = dados.get('lang','en-US')
    voz = VOZES.get(lang, 'en-US-JennyNeural')
    r = requests.get('https://edge.microsoft.com/translate/auth', headers={
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    })
    token = r.text
    ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="' + lang.split('-')[0] + '"><voice name="' + voz + '"><prosody rate="0%" pitch="0%">' + escapar(texto) + '</prosody></voice></speak>'
    
    headers = {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/ssml+xml',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
      'X-RequestId': uuid.uuid4().hex[:13],
      'X-Timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
    }
    
    audio = requests.post('https://speech.platform.bing.com/consumer/speech/synthesize/readaloud', headers=headers, data=ssml)
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tmp.write(audio.content)
    tmp.close()
    return send_file(tmp.name, mimetype='audio/mpeg')
  except Exception as e:
    return {'erro': str(e)}, 500
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
