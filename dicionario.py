import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import sys
import shutil
from datetime import datetime

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ---------------------------------------------------------------------------
# Tema e fontes
# ---------------------------------------------------------------------------

BG_MAIN           = "#0f1419"
BG_CARD           = "#1a1f2e"
BG_SEARCH_ENTRY   = "#242b3d"
FG_TEXT           = "#ffffff"
FG_SECONDARY      = "#8b96a5"
ACCENT_PRIMARY    = "#00d4ff"
ACCENT_SECONDARY  = "#7c3aed"

BTN_BLUE          = "#2563eb"
BTN_PURPLE        = "#7c3aed"
BTN_PINK          = "#ec4899"
BTN_GREEN         = "#10b981"
BTN_RED           = "#ef4444"
BTN_YELLOW        = "#f59e0b"
BTN_INDIGO        = "#6366f1"

FONT_DEFAULT  = ("Segoe UI", 11)
FONT_TITLE    = ("Segoe UI", 24, "bold")
FONT_SECTION  = ("Segoe UI", 14, "bold")
FONT_BUTTON   = ("Segoe UI", 10, "bold")
FONT_CODE     = ("Consolas", 11)

LIBS_FIXAS = ["pandas", "openpyxl", "numpy"]


# ---------------------------------------------------------------------------
# Caminhos e persistência
# ---------------------------------------------------------------------------

def resource_path(relative_path: str) -> str:
    """Retorna o caminho absoluto, compatível com PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, relative_path)


def _appdata_dir() -> str:
    if os.name == "nt":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.path.join(os.path.expanduser("~"), ".config")
    path = os.path.join(base, "DicionarioFreelancerTool")
    os.makedirs(path, exist_ok=True)
    return path


ARQUIVO_DADOS  = os.path.join(_appdata_dir(), "dados_app.json")
BUNDLE_JSON    = "dicionario completo.json"

DADOS_FALLBACK = {
    "bibliotecas": {
        "pandas": [
            {
                "nome": "pd.DataFrame",
                "desc": "Cria um DataFrame a partir de dicionários, listas ou arrays.",
                "tecnico": "df = pd.DataFrame({'Nome': ['Ana', 'João'], 'Idade': [25, 30]})",
                "pratico": "Cria uma tabela simples com nomes e idades para análise inicial.",
                "cat": "Criação de Estruturas de Dados",
            }
        ],
        "openpyxl": [
            {
                "nome": "Workbook",
                "desc": "Cria uma nova planilha Excel.",
                "tecnico": "wb = Workbook()",
                "pratico": "Inicia um novo arquivo Excel para relatórios ou dados.",
                "cat": "Escrita e Leitura",
            }
        ],
        "numpy": [
            {
                "nome": "np.array",
                "desc": "Cria um array NumPy a partir de listas ou iteráveis.",
                "tecnico": "arr = np.array([1, 2, 3, 4])",
                "pratico": "Útil para cálculos numéricos rápidos em arrays multidimensionais.",
                "cat": "Criação de Arrays",
            }
        ],
    },
    "historico": [],
}


def _carregar_bundle() -> dict | None:
    path = resource_path(BUNDLE_JSON)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if "bibliotecas" in dados and "historico" in dados:
            return dados
    except Exception as e:
        print(f"[AVISO] Falha ao ler bundle JSON: {e}")
    return None


def carregar_dados() -> dict:
    """Carrega dados do arquivo persistente, criando-o na primeira execução."""
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar dados: {e}. Usando fallback.")
            salvar_dados(DADOS_FALLBACK)
            return DADOS_FALLBACK

    # Primeira execução: tenta copiar o bundle empacotado
    bundle = _carregar_bundle()
    dados_iniciais = bundle if bundle else DADOS_FALLBACK
    bundle_path = resource_path(BUNDLE_JSON)
    if os.path.exists(bundle_path):
        try:
            shutil.copy2(bundle_path, ARQUIVO_DADOS)
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[AVISO] Falha ao copiar bundle: {e}")

    salvar_dados(dados_iniciais)
    return dados_iniciais


def salvar_dados(dados: dict) -> None:
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao salvar dados:\n{e}")


# ---------------------------------------------------------------------------
# Estado global
# ---------------------------------------------------------------------------

dados    = carregar_dados()
historico: list = dados["historico"]


# ---------------------------------------------------------------------------
# Utilitários de interface
# ---------------------------------------------------------------------------

def _btn(parent, text, command, bg, fg=FG_TEXT, **kwargs) -> tk.Button:
    defaults = dict(font=FONT_BUTTON, relief="flat", cursor="hand2")
    defaults.update(kwargs)
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg, **defaults)


def _section_header(parent, text, color) -> None:
    frame = tk.Frame(parent, bg=BG_MAIN)
    frame.pack(fill=tk.X, pady=(0, 10))
    tk.Label(frame, text=text, font=FONT_SECTION, bg=BG_MAIN, fg=color, anchor="w").pack(side=tk.LEFT)
    tk.Frame(frame, bg=color, height=2).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))


# ---------------------------------------------------------------------------
# Janela de texto genérica
# ---------------------------------------------------------------------------

def criar_janela_texto(titulo: str, texto: str, largura=800, altura=700) -> None:
    janela = tk.Toplevel(root)
    janela.title(titulo)
    janela.geometry(f"{largura}x{altura}")
    janela.resizable(True, True)
    janela.configure(bg=BG_MAIN)

    top = tk.Frame(janela, bg=BG_CARD)
    top.pack(fill=tk.X, padx=15, pady=10)

    def copiar():
        root.clipboard_clear()
        root.clipboard_append(texto)
        messagebox.showinfo("Copiado!", "Texto copiado para a área de transferência.")

    def exportar_pdf():
        _exportar_para_pdf(titulo, texto)

    _btn(top, "✨ Copiar Tudo",   copiar,          BTN_GREEN, padx=15, pady=8).pack(side=tk.LEFT,  padx=5)
    _btn(top, "📄 Exportar PDF",  exportar_pdf,    BTN_BLUE,  padx=15, pady=8).pack(side=tk.LEFT,  padx=5)
    _btn(top, "⛶ Maximizar",     lambda: janela.state("zoomed"), ACCENT_PRIMARY, "#000000", padx=15, pady=8).pack(side=tk.RIGHT, padx=5)
    _btn(top, "✖ Fechar",        janela.destroy,  BTN_RED,   padx=15, pady=8).pack(side=tk.RIGHT, padx=5)

    text_frame = tk.Frame(janela, bg=BG_MAIN)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    text_widget = tk.Text(
        text_frame, wrap=tk.WORD, font=FONT_CODE, padx=15, pady=15,
        bg=BG_CARD, fg=FG_TEXT, insertbackground=ACCENT_PRIMARY,
        selectbackground=ACCENT_SECONDARY, selectforeground=FG_TEXT,
        borderwidth=0, highlightthickness=1, highlightbackground=ACCENT_PRIMARY,
    )
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    text_widget.insert(tk.END, texto)
    text_widget.config(state=tk.DISABLED)

    scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget.config(yscrollcommand=scrollbar.set)

    def on_find(event=None):
        termo = simpledialog.askstring("Buscar", "Digite o termo:")
        if termo:
            text_widget.tag_remove("highlight", "1.0", tk.END)
            pos = text_widget.search(termo, "1.0", stopindex=tk.END)
            if pos:
                end = f"{pos}+{len(termo)}c"
                text_widget.tag_add("highlight", pos, end)
                text_widget.tag_config("highlight", background="#ffff00")
                text_widget.see(pos)

    janela.bind("<Control-f>", on_find)
    janela.transient(root)
    janela.grab_set()
    janela.wait_window()


# ---------------------------------------------------------------------------
# Exportar para PDF
# ---------------------------------------------------------------------------

def _exportar_para_pdf(titulo: str, texto: str) -> None:
    if not REPORTLAB_AVAILABLE:
        messagebox.showerror("Erro", "reportlab não instalado.\nInstale com: pip install reportlab")
        return

    pasta = os.path.join(os.path.expanduser("~"), "Desktop", "pdf_dicionario")
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_safe = titulo.replace(" ", "_").replace("/", "_")
    caminho = os.path.join(pasta, f"{nome_safe}_{timestamp}.pdf")

    c = canvas.Canvas(caminho, pagesize=letter)
    width, height = letter
    y = height - inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, titulo)
    y -= 30
    c.setFont("Helvetica", 11)

    for linha in texto.split("\n"):
        for trecho in [linha[i:i + 90] for i in range(0, max(len(linha), 1), 90)] or [""]:
            if y < inch:
                c.showPage()
                y = height - inch
            c.drawString(inch, y, trecho)
            y -= 15

    c.save()
    messagebox.showinfo("PDF Exportado!", f"Salvo em:\n{caminho}")


# ---------------------------------------------------------------------------
# Listar comandos
# ---------------------------------------------------------------------------

def _formatar_comando(cmd: dict) -> str:
    prioridade   = cmd.get("prioridade", "Não definida")
    fluxo        = ", ".join(cmd.get("fluxo_comum", [])) or "Nenhum"
    return (
        f"  > Nome: {cmd['nome']}\n"
        f"  > Descrição: {cmd['desc']} [Cat: {cmd.get('cat', 'N/A')}]\n"
        f"  > Prioridade: {prioridade}\n"
        f"  > Fluxo Comum: {fluxo}\n"
        f"  > Aplicação prática: {cmd['pratico']}\n"
        f"  > Exemplo técnico:\n"
        f"  {cmd['tecnico']}\n"
        f"\n{'-' * 80}\n\n"
    )


def show_list_window(titulo: str, comandos: list, lib_name: str) -> None:
    if not comandos:
        messagebox.showinfo(titulo, "Nenhum comando cadastrado ainda.")
        return
    corpo = "".join(_formatar_comando(c) for c in comandos)
    texto = f"Biblioteca: {lib_name}  —  Total de comandos: {len(comandos)}\n\n{corpo}"
    criar_janela_texto(titulo, texto, 1150, 900)


def listar_generica(lib_name: str) -> None:
    comandos = dados["bibliotecas"].get(lib_name, [])
    show_list_window(f"Comandos {lib_name.capitalize()}", comandos, lib_name.capitalize())


# ---------------------------------------------------------------------------
# Busca avançada
# ---------------------------------------------------------------------------

def buscar_comando_autocomplete(termo_inicial: str = "") -> None:

    def _match(cmd: dict, valor: str) -> bool:
        v = valor.lower()
        return (
            v in cmd["nome"].lower()
            or v in cmd["desc"].lower()
            or v in cmd["pratico"].lower()
        )

    def on_key(event):
        valor = entry.get()
        tree.delete(*tree.get_children())
        if not valor:
            return
        for lib_name, cmds in dados["bibliotecas"].items():
            for cmd in cmds:
                if _match(cmd, valor):
                    desc_trunc = cmd["desc"][:50] + ("..." if len(cmd["desc"]) > 50 else "")
                    tree.insert("", "end", values=(cmd["nome"], desc_trunc, cmd["cat"], lib_name.capitalize()))

    def on_select(event):
        sel = tree.selection()
        if sel:
            entry.delete(0, tk.END)
            entry.insert(0, tree.item(sel[0])["values"][0])
            tree.delete(*tree.get_children())

    def limpar():
        entry.delete(0, tk.END)
        tree.delete(*tree.get_children())

    def confirmar():
        termo = entry.get().strip()
        if not termo:
            messagebox.showwarning("Busca", "Digite um termo para buscar.")
            return

        resultados = {}
        for lib_name, cmds in dados["bibliotecas"].items():
            res = [
                (
                    f"{cmd['nome']} → {cmd['desc']} [{cmd['cat']}]\n"
                    f"Exemplo técnico:\n{cmd['tecnico']}\n"
                    f"Aplicação prática: {cmd['pratico']}\n"
                    f"\n{'-' * 60}\n\n"
                )
                for cmd in cmds if _match(cmd, termo)
            ]
            if res:
                resultados[lib_name] = res

        if resultados:
            texto = f"Resultados para '{termo}'\n"
            for lib, linhas in resultados.items():
                texto += f"\nBiblioteca {lib.capitalize()}:\n\n" + "".join(linhas)
        else:
            texto = "Nenhum comando encontrado."

        criar_janela_texto("Resultados da Busca", texto, 800, 700)

        try:
            import winsound
            winsound.Beep(600, 150)
        except Exception:
            pass

        dialog.destroy()

    dialog = tk.Toplevel(root)
    dialog.title("🔍 Busca Avançada")
    dialog.geometry("1100x750")
    dialog.resizable(True, True)
    dialog.configure(bg=BG_MAIN)

    header = tk.Frame(dialog, bg=BG_CARD)
    header.pack(fill=tk.X, padx=20, pady=15)
    tk.Label(header, text="🔍 Busca Inteligente de Comandos", font=FONT_SECTION, bg=BG_CARD, fg=ACCENT_PRIMARY).pack(pady=10)
    tk.Label(header, text="Busque por nome, descrição ou aplicação prática", font=FONT_DEFAULT, bg=BG_CARD, fg=FG_SECONDARY).pack(pady=(0, 10))

    entry_frame = tk.Frame(dialog, bg=BG_SEARCH_ENTRY)
    entry_frame.pack(fill=tk.X, padx=25, pady=10)
    tk.Label(entry_frame, text="🔍", font=("Segoe UI", 14), bg=BG_SEARCH_ENTRY, fg=ACCENT_PRIMARY).pack(side=tk.LEFT, padx=(10, 5), pady=10)
    entry = tk.Entry(entry_frame, width=50, font=("Segoe UI", 12), bg=BG_SEARCH_ENTRY, fg=FG_TEXT, insertbackground=ACCENT_PRIMARY, bd=0, highlightthickness=0)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=10, padx=(0, 10))
    entry.insert(0, termo_inicial)
    entry.bind("<KeyRelease>", on_key)
    entry.bind("<Return>", lambda e: confirmar())
    entry.focus()

    columns = ("Nome", "Descrição", "Categoria", "Biblioteca")
    tree = ttk.Treeview(dialog, columns=columns, show="headings", height=8)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#3c3c3c", foreground="white", fieldbackground="#3c3c3c", font=FONT_DEFAULT)
    style.map("Treeview", background=[("selected", "#555555")])

    tree.heading("Nome",       text="Nome");      tree.column("Nome",       width=150)
    tree.heading("Descrição",  text="Descrição"); tree.column("Descrição",  width=200)
    tree.heading("Categoria",  text="Categoria"); tree.column("Categoria",  width=100)
    tree.heading("Biblioteca", text="Biblioteca");tree.column("Biblioteca", width=100)

    tree.pack(pady=5, fill=tk.BOTH, expand=True)
    tree.bind("<<TreeviewSelect>>", on_select)

    scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.config(yscrollcommand=scrollbar.set)

    btn_frame = tk.Frame(dialog, bg=BG_MAIN)
    btn_frame.pack(pady=15, padx=25, fill=tk.X)
    _btn(btn_frame, "🧹 Limpar", limpar,    "#6b7280", padx=20, pady=10).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    _btn(btn_frame, "🔍 Buscar", confirmar, BTN_GREEN, padx=20, pady=10).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    dialog.transient(root)
    dialog.grab_set()
    dialog.wait_window()


# ---------------------------------------------------------------------------
# Gerenciamento de bibliotecas e comandos
# ---------------------------------------------------------------------------

def adicionar_nova_biblioteca() -> None:
    nome = simpledialog.askstring("Nova Biblioteca", "Nome da nova biblioteca (ex: requests):")
    if not nome:
        return
    nome = nome.lower()
    if nome in dados["bibliotecas"]:
        messagebox.showerror("Erro", f"A biblioteca '{nome}' já existe.")
        return
    dados["bibliotecas"][nome] = []
    historico.append(f"Adicionou biblioteca '{nome}'")
    salvar_dados(dados)
    recarregar_botoes_dicionarios(dicionarios_grid_dynamic)
    messagebox.showinfo("Sucesso", f"Biblioteca '{nome}' criada.\nUse 'Adicionar Comando' para inserir entradas.")


def remover_biblioteca() -> None:
    nome = simpledialog.askstring("Remover Biblioteca", "Nome da biblioteca a remover:")
    if not nome:
        return
    nome = nome.lower()
    if nome in LIBS_FIXAS:
        messagebox.showerror("Erro", f"'{nome}' é uma biblioteca padrão e não pode ser removida.")
        return
    if nome not in dados["bibliotecas"]:
        messagebox.showinfo("Remover", "Biblioteca não encontrada.")
        return
    if dados["bibliotecas"][nome]:
        messagebox.showerror("Erro", "Remova todos os comandos desta biblioteca antes de excluí-la.")
        return
    del dados["bibliotecas"][nome]
    historico.append(f"Removeu biblioteca '{nome}'")
    salvar_dados(dados)
    recarregar_botoes_dicionarios(dicionarios_grid_dynamic)
    messagebox.showinfo("Sucesso", f"Biblioteca '{nome}' removida.")


def adicionar_comando() -> None:
    dialog = tk.Toplevel(root)
    dialog.title("✨ Adicionar Novo Comando")
    dialog.geometry("750x950")
    dialog.resizable(True, True)
    dialog.configure(bg=BG_MAIN)
    dialog.transient(root)
    dialog.grab_set()

    top = tk.Frame(dialog, bg=BG_CARD)
    top.pack(fill=tk.X, padx=15, pady=10)
    _btn(top, "⛶ Maximizar", lambda: dialog.state("zoomed"), ACCENT_PRIMARY, "#000000", padx=15, pady=8).pack(side=tk.RIGHT, padx=5)
    _btn(top, "✖ Fechar",    dialog.destroy, BTN_RED, padx=15, pady=8).pack(side=tk.RIGHT, padx=5)

    tk.Label(dialog, text="📚 Selecione a Biblioteca", font=FONT_SECTION, bg=BG_MAIN, fg=ACCENT_PRIMARY).pack(pady=(10, 5))

    libs_card = tk.Frame(dialog, bg=BG_CARD, relief="flat")
    libs_card.pack(fill=tk.X, padx=20, pady=5)
    libs_str = "\n".join(f"{i+1}: {k.capitalize()}" for i, k in enumerate(dados["bibliotecas"]))
    tk.Label(libs_card, text=f"Digite o número da biblioteca:\n\n{libs_str}", font=FONT_DEFAULT, bg=BG_CARD, fg=FG_TEXT, justify=tk.LEFT).pack(pady=10, padx=15)

    lib_var = tk.StringVar()
    tk.Entry(dialog, textvariable=lib_var, font=("Segoe UI", 12), bg=BG_SEARCH_ENTRY, fg=FG_TEXT,
             insertbackground=ACCENT_PRIMARY, width=10, justify=tk.CENTER,
             bd=0, highlightthickness=2, highlightbackground=ACCENT_PRIMARY).pack(pady=10)

    fields = tk.Frame(dialog, bg=BG_MAIN)
    fields.pack(fill=tk.X, padx=20, pady=10)

    def _label(text):
        tk.Label(fields, text=text, font=FONT_DEFAULT, bg=BG_MAIN, fg=FG_SECONDARY, anchor="w").pack(fill=tk.X, pady=(5, 2))

    def _entry_single():
        e = tk.Entry(fields, width=50, font=("Segoe UI", 11), bg=BG_CARD, fg=FG_TEXT,
                     insertbackground=ACCENT_PRIMARY, bd=0, highlightthickness=1, highlightbackground=ACCENT_PRIMARY)
        e.pack(fill=tk.X, pady=(0, 10), ipady=8)
        return e

    def _entry_multi(height=3):
        e = tk.Text(fields, width=50, height=height, font=FONT_CODE, bg=BG_CARD, fg=FG_TEXT,
                    insertbackground=ACCENT_PRIMARY, bd=0, highlightthickness=1, highlightbackground=ACCENT_PRIMARY, padx=10, pady=8)
        e.pack(fill=tk.X, pady=(0, 10))
        return e

    _label("📝 Nome do comando:")
    nome_e = _entry_single()
    _label("💬 Descrição em Português:")
    desc_e = _entry_multi()
    _label("⚙️ Exemplo técnico:")
    tec_e  = _entry_multi()
    _label("💡 Aplicação prática:")
    prat_e = _entry_multi()
    _label("📂 Categoria:")
    cat_e  = _entry_single()

    def confirmar():
        try:
            idx = int(lib_var.get()) - 1
            lib_name = list(dados["bibliotecas"].keys())[idx]
        except (ValueError, IndexError):
            messagebox.showerror("Erro", "Número de biblioteca inválido.")
            return

        nome    = nome_e.get().strip()
        desc    = desc_e.get("1.0", tk.END).strip()
        tecnico = tec_e.get("1.0", tk.END).strip()
        pratico = prat_e.get("1.0", tk.END).strip()
        cat     = cat_e.get().strip()

        if not all([nome, desc, tecnico, pratico, cat]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
            return

        dados["bibliotecas"][lib_name].append({"nome": nome, "desc": desc, "tecnico": tecnico, "pratico": pratico, "cat": cat})
        historico.append(f"Adicionou '{nome}' em {lib_name.capitalize()}")
        salvar_dados(dados)
        messagebox.showinfo("Sucesso", f"Comando '{nome}' adicionado em {lib_name.capitalize()}.")
        dialog.destroy()

    btn_row = tk.Frame(dialog, bg=BG_MAIN)
    btn_row.pack(pady=10, padx=20, fill=tk.X)
    _btn(btn_row, "✅ Confirmar", confirmar,     BTN_GREEN, padx=20, pady=10).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    _btn(btn_row, "❌ Cancelar",  dialog.destroy, BTN_RED,   padx=20, pady=10).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    dialog.wait_window()


def remover_comando() -> None:
    nome = simpledialog.askstring("Remover Comando", "Nome do comando a remover:")
    if not nome:
        return
    for lib_name, cmds in dados["bibliotecas"].items():
        antes = len(cmds)
        dados["bibliotecas"][lib_name] = [c for c in cmds if c["nome"].lower() != nome.lower()]
        if len(dados["bibliotecas"][lib_name]) < antes:
            historico.append(f"Removeu '{nome}' de {lib_name.capitalize()}")
            salvar_dados(dados)
            messagebox.showinfo("Sucesso", f"Comando '{nome}' removido de {lib_name.capitalize()}.")
            return
    messagebox.showinfo("Remover", "Nenhum comando encontrado com esse nome.")


# ---------------------------------------------------------------------------
# Importar / Exportar JSON
# ---------------------------------------------------------------------------

def exportar_json() -> None:
    if not os.path.exists(ARQUIVO_DADOS):
        messagebox.showerror("Erro", "Nenhum dado para exportar.")
        return
    destino = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        title="Exportar Dicionário JSON",
    )
    if not destino:
        return
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as src:
            conteudo = json.load(src)
        with open(destino, "w", encoding="utf-8") as dst:
            json.dump(conteudo, dst, ensure_ascii=False, indent=2)
        historico.append(f"Exportou dicionário para {os.path.basename(destino)}")
        salvar_dados(dados)
        messagebox.showinfo("Sucesso", f"Exportado para:\n{destino}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao exportar:\n{e}")


def importar_json() -> None:
    origem = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")],
        title="Importar Dicionário JSON",
    )
    if not origem:
        return
    try:
        with open(origem, "r", encoding="utf-8") as f:
            novos = json.load(f)
        if "bibliotecas" not in novos or "historico" not in novos:
            raise ValueError("JSON inválido: precisa das chaves 'bibliotecas' e 'historico'.")
        global dados, historico
        dados     = novos
        historico = dados["historico"]
        salvar_dados(dados)
        recarregar_botoes_dicionarios(dicionarios_grid_dynamic)
        messagebox.showinfo("Sucesso", f"Importado de:\n{origem}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao importar:\n{e}")


# ---------------------------------------------------------------------------
# Histórico
# ---------------------------------------------------------------------------

def ver_historico() -> None:
    if not historico:
        messagebox.showinfo("Histórico", "Nenhuma ação registrada ainda.")
        return
    texto = "Últimas ações (mais recente no topo):\n\n" + "\n".join(historico[-20:][::-1])
    criar_janela_texto("Histórico de Ações", texto, 600, 500)


# ---------------------------------------------------------------------------
# Botões dinâmicos de bibliotecas
# ---------------------------------------------------------------------------

def recarregar_botoes_dicionarios(grid: tk.Frame) -> None:
    for w in grid.winfo_children():
        w.destroy()
    libs_dinamicas = sorted(k for k in dados["bibliotecas"] if k not in LIBS_FIXAS)
    for i, lib_name in enumerate(libs_dinamicas):
        row, col = divmod(i, 2)
        _btn(
            grid,
            text=f"📚 {lib_name.capitalize()}",
            command=lambda l=lib_name: listar_generica(l),
            bg=BTN_INDIGO,
            height=3,
        ).grid(row=row, column=col, padx=5, pady=5, sticky=tk.EW)


# ---------------------------------------------------------------------------
# Construção da interface principal
# ---------------------------------------------------------------------------

root = tk.Tk()
root.title("📖 Dicionário Freelancer Tool")
root.geometry("900x900")
root.resizable(True, True)
root.configure(bg=BG_MAIN)
root.columnconfigure(0, weight=1)

# Cabeçalho
title_frame = tk.Frame(root, bg=BG_MAIN)
title_frame.pack(pady=(25, 10), fill=tk.X)
tk.Label(title_frame, text="📖 Dicionário Freelancer Tool", font=FONT_TITLE, bg=BG_MAIN, fg=ACCENT_PRIMARY).pack()
tk.Label(title_frame, text="Seu assistente pessoal de programação Python", font=("Segoe UI", 10), bg=BG_MAIN, fg=FG_SECONDARY).pack()

# Barra de busca
search_frame = tk.Frame(root, bg=BG_MAIN)
search_frame.pack(fill=tk.X, padx=40, pady=(0, 25))
search_frame.columnconfigure(0, weight=1)

search_card = tk.Frame(search_frame, bg=BG_CARD, relief="flat", bd=0)
search_card.grid(row=0, column=0, sticky=tk.EW, padx=(0, 15))

search_entry_frame = tk.Frame(search_card, bg=BG_SEARCH_ENTRY, relief="flat")
search_entry_frame.pack(fill=tk.BOTH, padx=3, pady=3)
tk.Label(search_entry_frame, text="🔍", font=("Segoe UI", 14), bg=BG_SEARCH_ENTRY, fg=ACCENT_PRIMARY).pack(side=tk.LEFT, padx=(15, 10), pady=12)

PLACEHOLDER = "Digite para buscar comandos..."
search_var = tk.StringVar()
search_entry = tk.Entry(search_entry_frame, textvariable=search_var, width=35, font=("Segoe UI", 12),
                        bg=BG_SEARCH_ENTRY, fg=FG_SECONDARY, insertbackground=ACCENT_PRIMARY, bd=0, highlightthickness=0)
search_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=12)
search_entry.insert(0, PLACEHOLDER)


def _on_entry_click(event):
    if search_entry.get() == PLACEHOLDER:
        search_entry.delete(0, tk.END)
        search_entry.config(fg=FG_TEXT)


def _on_focusout(event):
    if search_entry.get() == "":
        search_entry.insert(0, PLACEHOLDER)
        search_entry.config(fg=FG_SECONDARY)


def on_buscar():
    termo = search_var.get().strip()
    if termo == PLACEHOLDER:
        termo = ""
    buscar_comando_autocomplete(termo)


search_entry.bind("<FocusIn>",  _on_entry_click)
search_entry.bind("<FocusOut>", _on_focusout)
search_entry.bind("<Return>",   lambda e: on_buscar())

_btn(search_frame, "🔍 Buscar", on_buscar, ACCENT_PRIMARY, "#000000", height=2, width=12, padx=20).grid(row=0, column=1, sticky=tk.E)

# Grade de ações (Gerenciamento | Dicionários)
actions_container = tk.Frame(root, bg=BG_MAIN, padx=30)
actions_container.pack(fill=tk.BOTH, expand=True, pady=(10, 20))
actions_container.columnconfigure(0, weight=1)
actions_container.columnconfigure(1, weight=1)

# --- Coluna esquerda ---
left_frame = tk.Frame(actions_container, bg=BG_MAIN)
left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=5)
left_frame.columnconfigure(0, weight=1)

_section_header(left_frame, "⚙️ Gerenciamento", ACCENT_PRIMARY)

gerenciar_card = tk.Frame(left_frame, bg=BG_CARD, relief="flat", bd=0)
gerenciar_card.pack(fill=tk.X, pady=(0, 25), padx=5)
gg = tk.Frame(gerenciar_card, bg=BG_CARD)
gg.pack(fill=tk.X, padx=10, pady=10)
gg.columnconfigure(0, weight=1); gg.columnconfigure(1, weight=1)

_btn(gg, "➕ Nova biblioteca",    adicionar_nova_biblioteca, BTN_BLUE,   height=3).grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
_btn(gg, "➖ Remover biblioteca", remover_biblioteca,        BTN_RED,    height=3).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
_btn(gg, "✨ Adicionar Comando",  adicionar_comando,         BTN_GREEN,  height=3).grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)
_btn(gg, "🗑️ Remover Comando",   remover_comando,           BTN_YELLOW, height=3).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

_section_header(left_frame, "🛠️ Utilitários", ACCENT_SECONDARY)

util_card = tk.Frame(left_frame, bg=BG_CARD, relief="flat", bd=0)
util_card.pack(fill=tk.X, pady=(0, 20), padx=5)
ug = tk.Frame(util_card, bg=BG_CARD)
ug.pack(fill=tk.X, padx=10, pady=10)
ug.columnconfigure(0, weight=1); ug.columnconfigure(1, weight=1)

_btn(ug, "🔍 Busca Avançada", on_buscar,     ACCENT_SECONDARY, height=3).grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
_btn(ug, "📅 Ver Histórico",  ver_historico, "#3b82f6",        height=3).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
_btn(ug, "📂 Importar JSON",  importar_json, BTN_PINK,         height=3).grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)
_btn(ug, "📤 Exportar JSON",  exportar_json, "#8b5cf6",        height=3).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

# --- Coluna direita ---
right_frame = tk.Frame(actions_container, bg=BG_MAIN)
right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=10, pady=5)
right_frame.columnconfigure(0, weight=1)

_section_header(right_frame, "📚 Dicionários", ACCENT_PRIMARY)

fixos_card = tk.Frame(right_frame, bg=BG_CARD, relief="flat", bd=0)
fixos_card.pack(fill=tk.X, pady=(0, 15), padx=5)
fg_grid = tk.Frame(fixos_card, bg=BG_CARD)
fg_grid.pack(fill=tk.X, padx=10, pady=10)
fg_grid.columnconfigure(0, weight=1); fg_grid.columnconfigure(1, weight=1)

_btn(fg_grid, "🐼 Pandas",   lambda: listar_generica("pandas"),   BTN_PURPLE, height=3).grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
_btn(fg_grid, "📄 Openpyxl", lambda: listar_generica("openpyxl"), BTN_PURPLE, height=3).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
_btn(fg_grid, "🔢 Numpy",    lambda: listar_generica("numpy"),    BTN_PURPLE, height=3).grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)

dynamic_card = tk.Frame(right_frame, bg=BG_CARD, relief="flat", bd=0)
dynamic_card.pack(fill=tk.BOTH, expand=True, padx=5)
dicionarios_grid_dynamic = tk.Frame(dynamic_card, bg=BG_CARD)
dicionarios_grid_dynamic.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
dicionarios_grid_dynamic.columnconfigure(0, weight=1)
dicionarios_grid_dynamic.columnconfigure(1, weight=1)

recarregar_botoes_dicionarios(dicionarios_grid_dynamic)

# Botão maximizar
max_frame = tk.Frame(root, bg=BG_MAIN)
max_frame.pack(pady=(15, 25), padx=40, fill=tk.X)
_btn(max_frame, "⛶ Maximizar Janela", lambda: root.state("zoomed"), BTN_GREEN, font=("Segoe UI", 13, "bold"), height=2).pack(fill=tk.X)

# Centralizar na tela
root.update_idletasks()
x = (root.winfo_screenwidth()  // 2) - (root.winfo_width()  // 2)
y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
root.geometry(f"+{x}+{y}")

root.mainloop()