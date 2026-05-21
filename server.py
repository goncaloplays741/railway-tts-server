import os, asyncio, json, traceback, tempfile
from flask import Flask, request, send_file
import edge_tts
app = Flask(__name__)
@app.route('/tts', methods=['POST'])
def tts():
    try:
        data = request.get_json(force=True)
        text = data.get('text', '')[:500]
        lang = data.get('lang', 'en-US')
        vozes = {
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
        voz = vozes.get(lang, 'en-US-JennyNeural')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def synth():
            c = edge_tts.Communicate(text, voz)
            f = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            async for chunk in c.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
            f.close()
            return f.name
        path = loop.run_until_complete(synth())
        loop.close()
        return send_file(path, mimetype='audio/mpeg')
    except Exception as e:
        return {'erro': str(e), 'trace': traceback.format_exc()}, 500
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
