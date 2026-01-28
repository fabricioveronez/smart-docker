# PRD - Agente Docker Analyzer

## 1. Visao Geral do Produto

### Nome
Agente Docker Analyzer

### Descricao
Agente de IA conversacional que recebe o diretorio raiz de um projeto de software, investiga autonomamente a estrutura (linguagem, frameworks, dependencias), localiza o Dockerfile e emite um parecer tecnico validando se o Dockerfile esta adequado ao projeto seguindo boas praticas de seguranca, performance e padronizacao.

### Contexto
Projeto pratico do video "LangChain para DevOps" que demonstra um agente que toma **multiplas decisoes autonomas** em sequencia: primeiro entende o projeto, depois valida o Dockerfile com base nesse entendimento.

---

## 2. Problema

Profissionais DevOps frequentemente revisam Dockerfiles manualmente, verificando se estao alinhados com o projeto. Isso inclui:
- A imagem base e adequada para a linguagem?
- O cache de layers esta otimizado?
- Ha problemas de seguranca (root, secrets)?
- O EXPOSE corresponde a porta real da aplicacao?

Um agente de IA pode automatizar essa revisao cruzando informacoes do projeto com o conteudo do Dockerfile.

---

## 3. Requisitos Funcionais

### RF-01: Receber diretorio via linha de comando
O usuario informa o caminho do projeto como argumento CLI:
```
python app.py /caminho/do/projeto
```

### RF-02: Investigar estrutura do projeto
O agente deve:
- Listar arquivos e pastas do diretorio raiz
- Navegar em subdiretorios quando necessario
- Identificar linguagem, framework e dependencias lendo arquivos-chave

### RF-03: Localizar e ler o Dockerfile
O agente deve encontrar o Dockerfile no projeto (raiz ou subdiretorios) e ler seu conteudo.

### RF-04: Analisar o Dockerfile no contexto do projeto
O agente deve cruzar o que entendeu do projeto com o Dockerfile e validar:

| Criterio | Descricao |
|----------|-----------|
| Imagem base | Adequada para linguagem/framework do projeto |
| Multi-stage build | Presente quando aplicavel (Go, Java, TypeScript) |
| Cache de layers | COPY de dependencias antes do COPY do codigo |
| Usuario nao-root | Instrucao USER definida |
| EXPOSE | Coerente com a porta da aplicacao |
| .dockerignore | Arquivo presente no projeto |
| Tamanho da imagem | Uso de variantes slim/alpine quando possivel |
| Seguranca | Sem secrets hardcoded, sem pacotes desnecessarios |

### RF-05: Retornar parecer estruturado
O agente deve retornar:
- Resumo do projeto identificado
- Lista de problemas encontrados no Dockerfile
- Sugestoes de melhoria com justificativa
- Nota geral (ex: "adequado com ressalvas", "precisa de ajustes")

### RF-06: Interface conversacional com memoria
Apos o parecer inicial, o usuario pode fazer perguntas de acompanhamento:
```
Voce: Pode detalhar o problema de cache de layers?
Agente: ...

Voce: Como ficaria o Dockerfile corrigido?
Agente: ...
```

A memoria da conversa deve ser mantida entre interacoes.

---

## 4. Requisitos Nao-Funcionais

### RNF-01: Stack de implementacao
- `create_agent` do `langchain.agents` para orquestrar o agente (API recomendada no LangChain v1, substitui o deprecado `create_react_agent` do `langgraph.prebuilt`)
- `argparse` para receber caminho via CLI
- Loop interativo com `input()`

### RNF-02: Abordagem de tools
Duas opcoes identificadas no levantamento tecnico (ver ESPECIFICACAO.md):

**Opcao A - Tools customizadas com @tool (recomendada)**
- Controle explicito sobre o que cada tool faz
- Mais didatico para o publico-alvo
- Nao precisa de dependencia extra

**Opcao B - FileManagementToolkit (langchain-community)**
- Toolkit pronto com `read_file`, `list_directory`, `file_search`
- Menos codigo, porem menos controle
- Requer pacote `langchain-community`

### RNF-03: LLM
Google Gemini 2.5 Flash via `langchain-google-genai`.

### RNF-04: Idioma
Todas as respostas do agente em portugues brasileiro.

---

## 5. Tools do Agente

Tres ferramentas de filesystem para o agente acessar o projeto:

### Tool 1: `listar_arquivos`
- **Input**: caminho do diretorio
- **Output**: lista de arquivos e pastas com metadados (tamanho)
- **Comportamento**: lista conteudo do diretorio informado (nao recursivo, o agente decide se navega mais fundo)

### Tool 2: `ler_arquivo`
- **Input**: caminho completo do arquivo
- **Output**: conteudo do arquivo como string
- **Comportamento**: le qualquer arquivo texto (Dockerfile, requirements.txt, package.json, .py, .go, .yaml, etc.)

### Tool 3: `buscar_arquivo`
- **Input**: diretorio raiz e nome/padrao do arquivo
- **Output**: lista de caminhos encontrados
- **Comportamento**: busca recursiva por nome (ex: encontrar Dockerfile em subdiretorios)

---

## 6. System Prompt

O system prompt deve instruir o agente a seguir este fluxo:

1. Listar arquivos do diretorio raiz para entender a estrutura
2. Identificar linguagem e framework lendo arquivos de dependencia
3. Localizar e ler o Dockerfile
4. Analisar o Dockerfile cruzando com o contexto do projeto
5. Retornar parecer estruturado

Criterios de analise que o prompt deve listar:
- Imagem base adequada para linguagem/framework
- Multi-stage build quando aplicavel
- Cache de layers (COPY de dependencias antes do codigo)
- Usuario nao-root
- EXPOSE coerente com a aplicacao
- .dockerignore presente
- Tamanho da imagem (slim/alpine)
- Seguranca (sem secrets hardcoded, sem pacotes desnecessarios)

---

## 7. Fluxo de Uso

```
$ python app.py /caminho/do/projeto

Analisando projeto: /caminho/do/projeto
Aguarde enquanto o agente investiga a estrutura...

Agente: [parecer completo]

Digite suas perguntas (ou 'sair' para encerrar)

Voce: Como ficaria o Dockerfile corrigido?
Agente: [resposta]

Voce: sair
Encerrando...
```

---

## 8. Estrutura de Arquivos

```
03-agente-docker/
  PRD.md              # Este documento
  ESPECIFICACAO.md    # Levantamento tecnico e referencias
  app.py              # Codigo do agente
  requirements.txt    # Dependencias
  .env.example        # Variaveis de ambiente (GOOGLE_API_KEY)
```

---

## 9. Dependencias

Para Opcao A (tools customizadas com @tool):
```
langchain>=1.2.3
langchain-google-genai>=4.2.0
python-dotenv>=1.0.0
```

Para Opcao B (FileManagementToolkit), adicionar:
```
langchain-community>=0.3.0
```

---

## 10. Projeto de Teste

Para validar o agente, usar o projeto existente no repositorio:

```
/home/fabricioveronez/projetos/youtube/02-subagentes-devops/01-aplicacao/eventos-tech/
```

Este projeto possui:
- Aplicacao Python/Flask
- `requirements.txt` com dependencias
- `Dockerfile` em `src/Dockerfile`
- Manifestos Kubernetes em `k8s/`

O agente deve ser capaz de identificar que e um projeto Python/Flask e validar o Dockerfile existente.

---

## 11. Criterios de Aceite

- [ ] Agente recebe diretorio via `python app.py /caminho`
- [ ] Agente lista a estrutura do projeto automaticamente
- [ ] Agente identifica linguagem e framework corretamente
- [ ] Agente encontra e le o Dockerfile
- [ ] Agente retorna parecer com problemas e sugestoes
- [ ] Conversa interativa com memoria funciona (follow-up questions)
- [ ] Funciona com o projeto `eventos-tech` como caso de teste
