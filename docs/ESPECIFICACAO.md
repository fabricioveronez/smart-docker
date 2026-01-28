# Especificacao - Agente Docker Analyzer

## Objetivo

Criar um agente LangChain que recebe o diretorio raiz de um projeto, investiga autonomamente a estrutura, entende a linguagem/frameworks/dependencias e valida se o Dockerfile esta adequado ao projeto seguindo boas praticas.

---

## Fluxo do Agente

```
Usuario informa diretorio raiz
        |
        v
[listar_arquivos] -> Mapeia estrutura do projeto
        |
        v
[ler_arquivo] -> Le arquivos-chave (requirements.txt, package.json, go.mod, etc.)
        |
        v
[buscar_arquivo] -> Localiza o Dockerfile (raiz ou subdiretorios)
        |
        v
[ler_arquivo] -> Le o Dockerfile
        |
        v
LLM analisa -> Cruza entendimento do projeto com conteudo do Dockerfile
        |
        v
Retorna parecer com sugestoes de melhoria
```

O agente decide **sozinho** quantas vezes e quais arquivos precisa ler. O loop de tool-calling (ReAct) permite multiplas iteracoes ate o agente ter informacao suficiente para dar o parecer.

---

## Arquitetura

### Componentes

| Componente | Tecnologia | Funcao |
|------------|-----------|--------|
| LLM | Google Gemini 2.5 Flash (via `langchain-google-genai`) | Raciocinio e analise |
| Agent | `create_agent` do `langchain.agents` | Orquestra loop ReAct de tool-calling |
| Tools | Customizadas com `@tool` | Acesso ao filesystem |
| System Prompt | Parametro `system_prompt` do `create_agent` | Guia comportamento do agente |

**Nota:** `create_agent` e a API recomendada no LangChain v1. O antigo `create_react_agent` do `langgraph.prebuilt` foi deprecado. `create_agent` roda sobre LangGraph internamente e oferece customizacao via middleware.

### Tools Customizadas

As tools sao criadas com o decorador `@tool` do `langchain_core.tools`.

| Tool | Input | Funcao |
|------|-------|--------|
| `listar_arquivos` | caminho do diretorio | Lista arquivos e pastas com metadados |
| `ler_arquivo` | caminho do arquivo | Le conteudo de qualquer arquivo texto |
| `buscar_arquivo` | diretorio + padrao | Busca recursiva por nome de arquivo |

### Duas abordagens possiveis (levantamento)

**Abordagem A - Tools customizadas com @tool**
- Mais didatico para o video
- Controle explicito sobre comportamento
- Nao precisa de `langchain-community`

**Abordagem B - FileManagementToolkit (alternativa)**
- LangChain fornece toolkit pronto com `read_file`, `list_directory`, etc.
- Menos codigo, porem menos controle
- Requer pacote `langchain-community`

### Nota sobre a inteligencia do agente

- A analise do Dockerfile esta no LLM, nao nas tools
- As tools sao apenas os "olhos e maos" do agente para acessar o filesystem
- O agente decide autonomamente quais arquivos ler e em que ordem

---

## Implementacao

### Dependencias

```
langchain>=1.2.3
langchain-google-genai>=4.2.0
python-dotenv>=1.0.0
```

Nota: `langchain>=1.2.3` ja inclui `create_agent` e `@tool`. O `langgraph` e instalado automaticamente como dependencia do `langchain`.

### Criacao do Agente

```python
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv

load_dotenv()

@tool
def listar_arquivos(caminho: str) -> str:
    """Lista arquivos e pastas do diretorio informado."""
    ...

@tool
def ler_arquivo(caminho_arquivo: str) -> str:
    """Le o conteudo completo de um arquivo."""
    ...

@tool
def buscar_arquivo(diretorio: str, nome: str) -> str:
    """Busca recursiva por nome de arquivo no diretorio."""
    ...

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
tools = [listar_arquivos, ler_arquivo, buscar_arquivo]

agent = create_agent(llm, tools=tools, system_prompt=SYSTEM_PROMPT)
```

### Invocacao

```python
resultado = agent.invoke(
    {"messages": [("human", pergunta)]}
)
resposta = resultado["messages"][-1].content
```

### System Prompt (direcionamento do agente)

O system prompt deve instruir o agente a:

1. Primeiro investigar a estrutura do projeto com `listar_arquivos`
2. Identificar linguagem, frameworks e dependencias lendo arquivos-chave
3. Localizar e ler o Dockerfile
4. Cruzar o entendimento do projeto com o conteudo do Dockerfile
5. Retornar um parecer estruturado

Exemplo de system prompt:

```
Voce e um especialista DevOps e Docker.

Seu objetivo e analisar um projeto de software e validar se o Dockerfile
esta adequado ao projeto, seguindo boas praticas.

Siga estes passos:
1. Liste os arquivos do diretorio raiz para entender a estrutura do projeto
2. Identifique a linguagem e framework lendo arquivos como requirements.txt,
   package.json, go.mod, pom.xml, etc.
3. Leia o Dockerfile do projeto
4. Analise o Dockerfile considerando:
   - Imagem base adequada para a linguagem/framework
   - Multi-stage build quando aplicavel
   - Cache de layers (COPY de dependencias antes do codigo)
   - Usuario nao-root
   - EXPOSE coerente com a aplicacao
   - .dockerignore presente
   - Tamanho da imagem (uso de slim/alpine)
   - Seguranca (sem secrets hardcoded, sem pacotes desnecessarios)
5. Retorne um parecer estruturado com problemas encontrados e sugestoes
```

---

## O que o Agente Consegue Validar (exemplos)

| Validacao | Como |
|-----------|------|
| Imagem base adequada | Le requirements.txt (Python) -> verifica se usa `python:x-slim` e nao `node:alpine` |
| Cache de layers | Verifica se `COPY requirements.txt .` vem antes de `COPY . .` |
| EXPOSE correto | Le codigo-fonte, identifica porta (ex: Flask 5000) -> verifica EXPOSE |
| Usuario nao-root | Verifica se existe instrucao `USER` no Dockerfile |
| Multi-stage build | Para projetos Go/Java, verifica se usa build stage separado |
| .dockerignore | Verifica se existe arquivo `.dockerignore` no projeto |
| Dependencias desnecessarias | Cruza dependencias do projeto com pacotes instalados no Dockerfile |
| Secrets expostos | Verifica se ha ENV com senhas ou tokens hardcoded |

---

## Fontes e Referencias da Documentacao

### LangChain - Criacao de Agentes
- [LangChain Agents - create_agent](https://docs.langchain.com/oss/python/langchain/agents) - API recomendada (v1) para criar agentes com tools
- [LangChain v1 Release Notes](https://docs.langchain.com/oss/python/releases/langchain-v1) - `create_agent` como padrao, substituindo `create_react_agent`
- [Migracao create_react_agent -> create_agent](https://docs.langchain.com/oss/python/migrate/langchain-v1) - Guia de migracao
- [Deprecacao create_react_agent](https://docs.langchain.com/oss/python/releases/langgraph-v1) - Nota de deprecacao
- [LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview) - Visao geral do framework

### LangChain - Tools e Filesystem
- [FileManagementToolkit](https://docs.langchain.com/oss/python/integrations/tools/filesystem) - Toolkit com `read_file`, `list_directory`, `write_file`, etc.
- [FilesystemFileSearchMiddleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in) - Middleware com `glob` e `grep` para busca em filesystem
- [Custom Tools com @tool](https://docs.langchain.com/oss/python/langchain/tools) - Decorador para criar tools customizadas (caso necessario)

### LangChain - Middleware e Customizacao
- [Decorator-based Middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom) - `@before_model`, `@wrap_tool_call`, `@dynamic_prompt`
- [Deep Agents - File System Access](https://docs.langchain.com/oss/python/deepagents/harness) - Tools de filesystem do Deep Agents (ls, read_file, glob, grep)
- [Deep Agents - Middleware](https://docs.langchain.com/oss/python/deepagents/middleware) - FilesystemMiddleware, TodoListMiddleware, SubAgentMiddleware

### LangGraph (orquestracao avancada)
- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview) - Framework de orquestracao de agentes (usado internamente pelo create_agent)
- [Agentic RAG com LangGraph](https://docs.langchain.com/oss/python/langgraph/agentic-rag) - Exemplo de agente com tool-calling customizado

### Estrutura de Projeto
- [File Structure - LangGraph](https://docs.langchain.com/oss/python/langgraph/application-structure) - Estrutura recomendada para projetos LangGraph
- [LangSmith Tool Server (MCP)](https://docs.langchain.com/langsmith/agent-builder-mcp-framework) - Framework MCP para tools com autenticacao

### Tutoriais Externos
- [LangChain Tools and Agents 2026](https://langchain-tutorials.github.io/langchain-tools-agents-2026/) - Patterns para producao

---

## Estrutura de Arquivos do Projeto

```
03-agente-docker/
  PRD.md             # Requisitos do produto
  ESPECIFICACAO.md   # Este arquivo (levantamento tecnico)
  app.py             # Codigo do agente
  requirements.txt   # Dependencias
  .env.example       # Variaveis de ambiente
```
