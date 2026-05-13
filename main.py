import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import google.generativeai as genai
import PIL.Image
import io

app = FastAPI()

# Mantenha sua API KEY configurada aqui
GOOGLE_API_KEY = "AIzaSyBivenejBRrYM8iSkxqM5BVZCAFnnQ7b-E"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CheckApp | Sistema Completo</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #f1f5f9; }
            .gradient-bg { background: linear-gradient(135deg, #1e1b4b 0%, #4338ca 100%); }
        </style>
    </head>
    <body>
        <nav class="bg-white border-b p-4 shadow-sm">
            <div class="max-w-4xl mx-auto flex justify-between items-center">
                <span class="font-bold text-xl text-indigo-900">CheckApp <span class="text-xs text-indigo-400">PRO DEMO</span></span>
                <div class="space-x-2">
                    <button onclick="switchTab('paciente')" class="px-4 py-2 font-medium text-indigo-600 bg-indigo-50 rounded-lg">Paciente</button>
                    <button onclick="switchTab('laboratorio')" class="px-4 py-2 font-medium text-slate-600 hover:bg-slate-100 rounded-lg">Laboratório</button>
                </div>
            </div>
        </nav>

        <main class="max-w-3xl mx-auto p-6">
            <div id="tab-paciente">
                <div class="bg-white rounded-3xl shadow-xl p-8 border border-slate-100">
                    <h2 class="text-xl font-bold mb-6">Busca de Exames</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        <input id="cep" type="text" placeholder="CEP (ex: 01001-000)" class="p-4 border rounded-xl">
                        <select id="exame-manual" class="p-4 border rounded-xl bg-white">
                            <option value="Hemograma">Hemograma Completo</option>
                            <option value="Vitamina D">Vitamina D</option>
                            <option value="Glicemia">Glicemia de Jejum</option>
                            <option value="USG Abdomen">USG Abdomen Total</option>
                            <option value="Ressonancia">Ressonância Magnética</option>
                            <option value="Tomografia">Tomografia Computadorizada</option>
                            <option value="Raio-X">Raio-X Tórax</option>
                        </select>
                    </div>
                    <label for="foto-receita" class="block w-full border-2 border-dashed border-indigo-300 p-6 rounded-2xl text-center cursor-pointer hover:border-indigo-500">
                        📸 Selecionar/Tirar foto do pedido médico
                        <input type="file" id="foto-receita" class="hidden" accept="image/*" onchange="processarIA()">
                    </label>
                    <div id="loading" class="hidden mt-4 text-indigo-600 font-bold text-center animate-pulse">Analisando receita...</div>
                    <div id="resultado" class="hidden mt-6 p-4 bg-emerald-50 rounded-xl border border-emerald-200">
                        Exame detectado: <span id="exame-detectado" class="font-bold"></span>
                    </div>
                </div>
            </div>

            <div id="tab-laboratorio" class="hidden">
                <div class="bg-slate-900 text-white rounded-3xl p-8 shadow-2xl">
                    <h2 class="text-xl font-bold mb-6">Painel de Configurações (Laboratório)</h2>
                    <div class="space-y-4">
                        <div>
                            <label class="text-xs text-slate-400 block mb-1">Margem máxima de desconto (%)</label>
                            <input id="desconto" type="number" value="20" class="w-full bg-slate-800 p-3 rounded-lg border border-slate-700">
                        </div>
                        <div>
                            <label class="text-xs text-slate-400 block mb-1">Horários de "Agenda Ociosa"</label>
                            <input id="horarios" type="text" value="13:00 - 17:00" class="w-full bg-slate-800 p-3 rounded-lg border border-slate-700">
                        </div>
                        <button onclick="salvarConfig()" class="w-full bg-emerald-600 text-white font-bold py-3 rounded-lg mt-4 hover:bg-emerald-700">SALVAR CONFIGURAÇÕES</button>
                        <p id="msg-sucesso" class="text-emerald-400 text-sm mt-2 hidden text-center">Configurações salvas com sucesso!</p>
                    </div>
                </div>
            </div>
        </main>

        <script>
            function switchTab(t) {
                document.getElementById('tab-paciente').style.display = t === 'paciente' ? 'block' : 'none';
                document.getElementById('tab-laboratorio').style.display = t === 'laboratorio' ? 'block' : 'none';
            }
            function salvarConfig() {
                document.getElementById('msg-sucesso').classList.remove('hidden');
                setTimeout(() => document.getElementById('msg-sucesso').classList.add('hidden'), 2000);
            }
            async function processarIA() {
                const input = document.getElementById('foto-receita');
                if (!input.files[0]) return;
                document.getElementById('loading').classList.remove('hidden');
                const fd = new FormData(); fd.append('file', input.files[0]);
                const res = await fetch('/ia-scan', { method: 'POST', body: fd });
                const data = await res.json();
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('resultado').classList.remove('hidden');
                document.getElementById('exame-detectado').innerText = data.exame;
            }
        </script>
    </body>
    </html>
    """

@app.post("/ia-scan")
async def scan_receita(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = PIL.Image.open(io.BytesIO(contents))
        # PROMPT MELHORADO E MAIS ESPECÍFICO
        prompt = "Analise esta imagem de pedido médico. Identifique o nome do exame. Retorne APENAS o nome em MAIÚSCULAS. Se não encontrar, retorne 'EXAME NÃO IDENTIFICADO'."
        response = model.generate_content([prompt, img])
        return {"exame": response.text.strip()}
    except Exception as e:
        return {"exame": "Erro ao ler imagem. Tente outra."}
