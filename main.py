import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import PIL.Image
import io

app = FastAPI()

# CONFIGURAÇÃO DA IA (Mantenha sua chave aqui)
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
        <title>CheckApp | Plataforma Integrada</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #f1f5f9; }
            .gradient-bg { background: linear-gradient(135deg, #1e1b4b 0%, #4338ca 100%); }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <nav class="bg-white border-b p-4 shadow-sm">
            <div class="max-w-4xl mx-auto flex justify-between items-center">
                <span class="font-bold text-xl text-indigo-900">CheckApp</span>
                <div class="space-x-2">
                    <button onclick="switchTab('paciente')" class="px-4 py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50 rounded-lg">Paciente</button>
                    <button onclick="switchTab('laboratorio')" class="px-4 py-2 text-sm font-medium bg-slate-800 text-white rounded-lg">Laboratório</button>
                </div>
            </div>
        </nav>

        <main class="max-w-3xl mx-auto p-6 mt-6">
            
            <div id="tab-paciente">
                <div class="bg-white rounded-3xl shadow-xl p-8 border border-slate-100">
                    <h2 class="text-2xl font-bold text-slate-800 mb-6">Encontrar Exames</h2>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        <input id="cep" type="text" placeholder="Seu CEP" class="p-4 border rounded-xl outline-none focus:ring-2 focus:ring-indigo-500">
                        <select id="exame-manual" class="p-4 border rounded-xl outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="Hemograma">Hemograma Completo</option>
                            <option value="Vitamina D">Vitamina D</option>
                            <option value="Glicemia">Glicemia de Jejum</option>
                        </select>
                    </div>

                    <div class="flex items-center gap-4 mb-6">
                        <button onclick="simularLeilao()" class="flex-1 bg-indigo-600 text-white font-bold py-4 rounded-xl shadow-lg hover:bg-indigo-700 transition">BUSCAR MANUALMENTE</button>
                        <span class="text-slate-400 font-bold">OU</span>
                        <label for="foto-receita" class="flex-1 border-2 border-indigo-600 text-indigo-600 font-bold py-4 rounded-xl text-center cursor-pointer hover:bg-indigo-50 transition">
                            FOTO DA RECEITA
                            <input type="file" id="foto-receita" class="hidden" accept="image/*" onchange="processarIA()">
                        </label>
                    </div>

                    <div id="loading" class="hidden text-center py-8">
                        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                        <p id="status-txt" class="text-indigo-600 font-medium">Processando...</p>
                    </div>

                    <div id="resultado-uber" class="hidden space-y-4 pt-6 border-t">
                        <h3 class="font-bold text-slate-700 mb-4">Lances Ganhadores:</h3>
                        <div class="border-2 border-emerald-500 bg-white p-6 rounded-2xl flex justify-between items-center shadow-md">
                            <div>
                                <h4 class="font-bold text-slate-800">CheckApp Express (Ociosidade)</h4>
                                <p class="text-xs text-slate-500">Unidade no seu CEP - Hoje 14:30</p>
                            </div>
                            <div class="text-right">
                                <div id="price-express" class="text-2xl font-black text-emerald-600">R$ --</div>
                                <div class="text-[10px] bg-emerald-100 text-emerald-700 px-2 py-1 rounded font-bold uppercase">30% OFF</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div id="tab-laboratorio" class="hidden">
                <div class="bg-slate-900 text-white rounded-3xl p-8 shadow-2xl">
                    <h2 class="text-2xl font-bold mb-6">Painel de Ociosidade (B2B)</h2>
                    <div class="grid grid-cols-2 gap-4 mb-8">
                        <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                            <p class="text-[10px] uppercase font-bold text-slate-500 mb-1">Status do Leilão</p>
                            <p class="text-emerald-400 font-bold">Ativo & Recebendo</p>
                        </div>
                        <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                            <p class="text-[10px] uppercase font-bold text-slate-500 mb-1">Yield Management</p>
                            <p class="font-bold">Max 30% Desconto</p>
                        </div>
                    </div>
                    <p class="text-xs text-slate-400">Configure aqui os períodos de ociosidade para baixar os preços automaticamente e ocupar a agenda.</p>
                </div>
            </div>
        </main>

        <script>
            function switchTab(tab) {
                document.getElementById('tab-paciente').classList.toggle('hidden', tab !== 'paciente');
                document.getElementById('tab-laboratorio').classList.toggle('hidden', tab !== 'laboratorio');
            }

            async function processarIA() {
                const fileInput = document.getElementById('foto-receita');
                if (!fileInput.files[0]) return;
                
                document.getElementById('loading').classList.remove('hidden');
                document.getElementById('status-txt').innerText = "Gemini analisando receita...";
                
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                const response = await fetch('/ia-scan', { method: 'POST', body: formData });
                const data = await response.json();
                exibirResultados(data.exame);
            }

            function simularLeilao() {
                const exame = document.getElementById('exame-manual').value;
                document.getElementById('loading').classList.remove('hidden');
                document.getElementById('status-txt').innerText = "Buscando lances no seu CEP...";
                setTimeout(() => exibirResultados(exame), 1500);
            }

            function exibirResultados(exame) {
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('resultado-uber').classList.remove('hidden');
                let base = exame.includes("Hemograma") ? 30 : 100;
                document.getElementById('price-express').innerText = "R$ " + (base * 0.7).toFixed(2);
            }
        </script>
    </body>
    </html>
    """

@app.post("/ia-scan")
async def scan_receita(file: UploadFile = File(...)):
    contents = await file.read()
    img = PIL.Image.open(io.BytesIO(contents))
    prompt = "Identifique o exame laboratorial principal. Responda apenas o nome em MAIÚSCULAS."
    response = model.generate_content([prompt, img])
    return {"exame": response.text.strip()}
