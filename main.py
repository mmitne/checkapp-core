import os
import io
import PIL.Image
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import google.generativeai as genai

app = FastAPI(title="CheckApp Pro")

# --- CONFIGURAÇÃO DA IA ---
# O sistema busca a chave nas variáveis de ambiente do Render (Seguro e Profissional)
api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CheckApp | O Futuro dos Exames</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
            .gradient-bg { background: linear-gradient(135deg, #1e1b4b 0%, #d946ef 100%); }
            .glass-card { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }
            .btn-gradient { background: linear-gradient(135deg, #1e1b4b 0%, #d946ef 100%); transition: transform 0.2s; }
            .btn-gradient:hover { transform: scale(1.02); }
        </style>
    </head>
    <body class="min-h-screen">

        <header class="gradient-bg text-white p-6 shadow-lg">
            <div class="max-w-4xl mx-auto flex justify-between items-center">
                <h1 class="text-3xl font-black tracking-tight">Check<span class="text-pink-300">App</span></h1>
                <nav class="space-x-4">
                    <button onclick="showTab('paciente')" class="hover:text-pink-200 font-bold">Paciente</button>
                    <button onclick="showTab('laboratorio')" class="hover:text-pink-200 font-bold">Laboratório</button>
                </nav>
            </div>
        </header>

        <main class="max-w-4xl mx-auto p-6 -mt-10">
            
            <div id="tab-paciente" class="glass-card rounded-3xl shadow-2xl p-8 border border-slate-100">
                <h2 class="text-2xl font-bold text-slate-800 mb-6">Solicitação de Exames</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div>
                        <label class="text-xs font-bold text-slate-500 uppercase">CEP do Atendimento</label>
                        <input id="cep" type="text" placeholder="00000-000" class="w-full mt-2 p-4 border border-slate-200 rounded-xl focus:ring-2 focus:ring-pink-500 outline-none">
                    </div>
                    <div>
                        <label class="text-xs font-bold text-slate-500 uppercase">Selecione o Exame</label>
                        <select id="exame-manual" class="w-full mt-2 p-4 border border-slate-200 rounded-xl bg-white focus:ring-2 focus:ring-pink-500 outline-none">
                            <option value="Hemograma">Hemograma Completo</option>
                            <option value="Vitamina D">Vitamina D</option>
                            <option value="Glicemia">Glicemia de Jejum</option>
                            <option value="USG Abdomen">USG Abdomen Total</option>
                            <option value="Ressonancia">Ressonância Magnética</option>
                            <option value="Tomografia">Tomografia Computadorizada</option>
                            <option value="Raio-X">Raio-X Tórax</option>
                        </select>
                    </div>
                </div>

                <div class="border-2 border-dashed border-indigo-200 rounded-2xl p-8 text-center bg-indigo-50/50 hover:border-pink-400 transition cursor-pointer">
                    <input type="file" id="foto-receita" class="hidden" accept="image/*" onchange="processarIA()">
                    <label for="foto-receita" class="cursor-pointer">
                        <span class="block text-4xl mb-2">📸</span>
                        <span class="font-bold text-indigo-900">Upload da Receita Médica</span>
                        <p class="text-xs text-slate-500 mt-1">Nossa IA lê sua receita em segundos</p>
                    </label>
                </div>

                <div id="loading" class="hidden mt-8 text-center py-4 bg-indigo-50 rounded-xl text-indigo-700 font-bold animate-pulse">
                    Conectando com o Gemini... Analisando imagem...
                </div>

                <div id="resultado" class="hidden mt-8 p-6 bg-emerald-50 rounded-2xl border border-emerald-200">
                    <p class="text-sm text-emerald-800 font-bold uppercase tracking-wider">Exame Identificado:</p>
                    <p id="exame-nome" class="text-3xl font-black text-emerald-900 mt-1">---</p>
                    <div class="mt-4 pt-4 border-t border-emerald-200 flex justify-between items-center">
                        <span class="text-sm text-emerald-700">Preço com desconto:</span>
                        <span class="text-2xl font-black text-emerald-600">R$ 145,00</span>
                    </div>
                </div>
            </div>

            <div id="tab-laboratorio" class="hidden glass-card rounded-3xl shadow-2xl p-8 border border-slate-100">
                <h2 class="text-2xl font-bold text-slate-800 mb-2">Painel de Controle B2B</h2>
                <p class="text-slate-500 mb-8">Gerencie sua ociosidade de agenda.</p>
                
                <div class="space-y-6">
                    <div class="p-6 bg-slate-900 rounded-2xl text-white">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="text-xs text-slate-400">Margem Max de Desconto (%)</label>
                                <input id="lab-desconto" type="number" value="30" class="w-full mt-1 bg-slate-800 p-3 rounded-lg border border-slate-700 text-white font-bold">
                            </div>
                            <div>
                                <label class="text-xs text-slate-400">Horário Ocioso</label>
                                <input id="lab-horario" type="text" value="13:00 - 17:00" class="w-full mt-1 bg-slate-800 p-3 rounded-lg border border-slate-700 text-white font-bold">
                            </div>
                        </div>
                        <button onclick="salvarConfig()" class="w-full mt-6 bg-pink-600 text-white font-bold py-4 rounded-xl hover:bg-pink-700 transition">SALVAR REGRAS DE NEGÓCIO</button>
                        <p id="save-msg" class="hidden mt-3 text-emerald-400 text-center font-bold">Regras salvas na nuvem!</p>
                    </div>
                </div>
            </div>
        </main>

        <script>
            function showTab(tab) {
                document.getElementById('tab-paciente').style.display = tab === 'paciente' ? 'block' : 'none';
                document.getElementById('tab-laboratorio').style.display = tab === 'laboratorio' ? 'block' : 'none';
            }
            function salvarConfig() {
                document.getElementById('save-msg').classList.remove('hidden');
                setTimeout(() => document.getElementById('save-msg').classList.add('hidden'), 3000);
            }
            async function processarIA() {
                const input = document.getElementById('foto-receita');
                if (!input.files[0]) return;
                document.getElementById('loading').classList.remove('hidden');
                document.getElementById('resultado').classList.add('hidden');
                
                const fd = new FormData();
                fd.append('file', input.files[0]);

                try {
                    const res = await fetch('/ia-scan', { method: 'POST', body: fd });
                    const data = await res.json();
                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('resultado').classList.remove('hidden');
                    document.getElementById('exame-nome').innerText = data.exame;
                } catch (e) {
                    alert("Erro na leitura. Tente novamente.");
                    document.getElementById('loading').classList.add('hidden');
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/ia-scan")
async def scan_receita(file: UploadFile = File(...)):
    if not model:
        return {"exame": "ERRO: CHAVE API NÃO CONFIGURADA"}
    
    try:
        contents = await file.read()
        img = PIL.Image.open(io.BytesIO(contents))
        prompt = "Analise o pedido médico e identifique o exame principal. Responda APENAS o nome do exame em MAIÚSCULAS. Se for exame de imagem (Ressonância, Tomografia, USG), identifique também. Resposta curta."
        response = model.generate_content([prompt, img])
        return {"exame": response.text.strip()}
    except Exception as e:
        return {"exame": "NÃO FOI POSSÍVEL LER A IMAGEM"}
