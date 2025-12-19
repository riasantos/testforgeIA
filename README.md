🚀 TestForge: AI-Driven Test Case Generator
TestForge é uma ferramenta avançada de automação para Engenheiros de QA que utiliza a inteligência do GitHub Copilot (GPT-4) para transformar documentos de requisitos (.docx) em planos de teste detalhados e prontos para execução em formato Excel.

🌟 Funcionalidades
Extração Automática: Lê requisitos diretamente de arquivos Word, identificando seções e regras de negócio.

Inteligência de QA: Gera cenários baseados em técnicas reais:

Particionamento de Equivalência.

Análise de Valor Limite.

Happy Path e Fluxos de Exceção.

Testes de Segurança e Performance.

Exportação Inteligente: Consolida todos os cenários em um arquivo Excel (.xlsx) organizado com uma aba por documento.

Métricas Integradas: Calcula automaticamente o tempo economizado e a estimativa de bugs prováveis.

Pronto para CI/CD: Integração nativa com GitHub Actions para geração automática em pipeline.

🏗️ Arquitetura do Projeto
O fluxo de dados do TestForge segue uma estrutura lógica de pipeline:

Ingestão: O script varre a pasta /Documentações em busca de arquivos .docx.

Processamento: O conteúdo é limpo e estruturado em um prompt otimizado para a API do Copilot.

IA: O modelo processa os requisitos e retorna um JSON técnico rigoroso.

Entrega: Os dados são validados e formatados em uma planilha Excel profissional.

🛠️ Instalação e Uso
Pré-requisitos
Python 3.10+

Um Token de Acesso do GitHub (com permissão para Copilot)

Configuração
Clone o repositório:

Bash

git clone https://github.com/seu-usuario/testforge.git
cd testforge
Instale as dependências:

Bash

pip install -r requirements.txt
Configure sua chave de API:

Bash

export GITHUB_TOKEN="seu_token_aqui"
Execução
Coloque seus arquivos de requisitos na pasta Documentações/ e execute:

Bash

python src/main.py
⚙️ CI/CD com GitHub Actions
Este projeto está configurado para rodar automaticamente via GitHub Actions. Sempre que um novo requisito é adicionado à branch main, o pipeline:

Instala o ambiente Python.

Executa o TestForge.

Disponibiliza o Plano de Testes gerado como um Artifact para download.

Nota: Certifique-se de configurar o COPILOT_TOKEN em Settings > Secrets > Actions no seu repositório.

📈 Roadmap & Melhorias Futuras
[ ] Suporte para leitura de arquivos PDF.

[ ] Integração direta com Jira/Xray via API.

[ ] Processamento paralelo para grandes volumes de documentos.

[ ] Dashboard visual de cobertura de requisitos.

📄 Licença
Distribuído sob a licença MIT. Veja LICENSE para mais informações.