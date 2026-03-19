# 📖 Dicionário Freelancer Tool

Aplicação desktop para consulta rápida de comandos Python durante projetos freelancer. Reúne em um único lugar descrições, exemplos técnicos e aplicações práticas das bibliotecas mais usadas em automação de dados.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python) ![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational) ![License](https://img.shields.io/badge/license-MIT-green)

---

## Motivação

Durante projetos freelancer com pandas, openpyxl e numpy, perco tempo voltando à documentação oficial para lembrar sintaxes que já usei antes. Essa ferramenta funciona como um dicionário pessoal e editável: busco o comando, vejo o exemplo e sigo em frente.

---

## Funcionalidades

- **Busca inteligente** por nome, descrição ou aplicação prática, com autocomplete em tempo real
- **Bibliotecas pré-carregadas**: Pandas, Openpyxl e Numpy com dezenas de comandos cada
- **Bibliotecas customizadas**: adicione qualquer biblioteca com seus próprios comandos
- **Exportação para PDF** de qualquer lista (via reportlab)
- **Importar / Exportar JSON** — leve seu dicionário entre máquinas
- **Histórico de ações** das últimas 20 operações
- **Build para .exe** via PyInstaller com JSON embutido

---

## Screenshots

**Tela inicial** — busca rápida, gerenciamento de bibliotecas e acesso aos dicionários

![Tela inicial](screenshots/Tela_inicial.png)

**Adicionar comando** — formulário com nome, descrição em português, exemplo técnico e aplicação prática

![Adicionar comando](screenshots/Adicionar_novo_comando.png)

**Lista de comandos** — visualização completa com exportação para PDF e cópia para clipboard

![Lista de comandos](screenshots/Lista_de_comandos.png)

---

## Requisitos

- Python 3.10+
- `reportlab` (opcional, apenas para exportar PDF)

```bash
pip install reportlab
```

---

## Como executar

```bash
# Clonar o repositório
git clone https://github.com/joaopedoni-dev/dicionario-freelancer-tool.git
cd dicionario-freelancer-tool

# Executar direto
python Dicionario_Freelancer_Tool.py
```

Os dados são salvos automaticamente em:

| Sistema | Caminho |
|---------|---------|
| Windows | `%APPDATA%\DicionarioFreelancerTool\dados_app.json` |
| Linux / macOS | `~/.config/DicionarioFreelancerTool/dados_app.json` |

---

## Gerar executável (.exe)

```bash
pip install pyinstaller

pyinstaller --onefile --windowed \
  --add-data "dicionario.json;." \
  --name "DicionarioFreelancerTool" \
  Dicionario_Freelancer_Tool.py
```

O executável gerado em `dist/` já embute o JSON com todos os comandos. Na primeira execução, os dados são copiados para o AppData do usuário, permitindo edição persistente.

---

## Estrutura do JSON

Cada entrada segue este formato:

```json
{
  "nome": "pd.merge",
  "desc": "Une dois DataFrames com base em colunas comuns.",
  "tecnico": "df = pd.merge(df1, df2, on='id', how='left')",
  "pratico": "Combina tabela de clientes com tabela de pedidos pelo ID.",
  "cat": "Combinação de Dados",
  "prioridade": "Essencial",
  "fluxo_comum": ["Transformação", "Junção"]
}
```

Os campos `prioridade` e `fluxo_comum` são opcionais — comandos sem eles são exibidos normalmente.

---

## Tecnologias

| Tecnologia | Uso |
|------------|-----|
| Python / Tkinter | Interface gráfica desktop |
| JSON | Persistência dos dados |
| reportlab | Exportação para PDF |
| PyInstaller | Empacotamento para .exe |

---

## Licença

MIT — veja [LICENSE](LICENSE.txt)
