# SmartDocker

Agente de IA que analisa Dockerfiles de projetos de software, identificando problemas de seguranca, performance e boas praticas. O agente investiga autonomamente a estrutura do projeto, identifica a linguagem e framework utilizados e gera um relatorio completo com problemas encontrados e sugestoes de correcao.

## Como funciona

1. O agente lista os arquivos do projeto para entender a estrutura
2. Identifica a linguagem e framework lendo arquivos de dependencia
3. Localiza e le o Dockerfile do projeto
4. Analisa o Dockerfile com base em 8 criterios de qualidade
5. Gera um relatorio em Markdown com problemas e sugestoes

### Criterios de analise

- **Imagem base** - Compatibilidade com a linguagem/framework do projeto
- **Multi-stage build** - Presente quando aplicavel (Go, Java, TypeScript)
- **Cache de layers** - COPY de dependencias antes do codigo fonte
- **Usuario nao-root** - Instrucao USER definida no Dockerfile
- **EXPOSE** - Coerencia com a porta real da aplicacao
- **.dockerignore** - Arquivo presente no projeto
- **Tamanho da imagem** - Uso de variantes slim/alpine
- **Seguranca** - Sem secrets hardcoded, sem pacotes desnecessarios

## Tecnologias

- **Python 3**
- **LangChain** - Framework de agentes com tool-calling
- **Google Gemini 2.5 Flash** - LLM utilizado pelo agente
- **FileManagementToolkit** - Tools para leitura e busca de arquivos

## Pre-requisitos

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) - Gerenciador de pacotes Python
- Chave de API do Google Gemini

## Instalacao

```bash
uv sync
```

Configure a variavel de ambiente com sua chave de API:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave:

```
GOOGLE_API_KEY=sua-chave-aqui
```

## Uso

```bash
uv run smart-docker /caminho/do/projeto
```

Para especificar o arquivo de saida:

```bash
uv run smart-docker /caminho/do/projeto -o meu-relatorio.md
```

Ou execute diretamente:

```bash
uv run python src/app.py /caminho/do/projeto
```

## Estrutura do projeto

```
.
├── docs/
│   ├── ESPECIFICACAO.md  # Especificacao tecnica detalhada
│   └── PRD.md            # Product Requirements Document
├── src/
│   ├── __init__.py       # Inicializador do pacote
│   ├── app.py            # Ponto de entrada e orquestracao do agente
│   ├── prompt.py         # System prompt com instrucoes de analise
│   └── tools.py          # Configuracao das tools do agente
├── .env.example          # Template de variaveis de ambiente
├── pyproject.toml        # Configuracao do projeto e dependencias
├── uv.lock               # Lock file com versoes exatas
└── README.md             # Este arquivo
```

## Exemplo de saida

O agente gera um relatorio em Markdown com a seguinte estrutura:

- **Resumo do Projeto** - Linguagem, framework, estrutura e dependencias
- **Problemas Encontrados** - Lista de problemas com severidade e solucao
- **Dockerfile Sugerido** - Versao corrigida aplicando todas as melhorias
- **Nota Geral** - Avaliacao: adequado, adequado com ressalvas ou precisa de ajustes
