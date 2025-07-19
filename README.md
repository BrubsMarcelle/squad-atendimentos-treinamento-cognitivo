# Sistema de Treinamento Cognitivo da Squad Atendimentos

Este projeto é uma aplicação destinada a fornecer um ranking treinamento cognitivo da squad de atendimento, com o objetivo de que todos possam fazer o treinamento da ferramenta IA.

---



## 🚀 Como Rodar o Projeto Localmente

Siga os passos abaixo para configurar e executar a aplicação em seu ambiente de desenvolvimento.

### Pré-requisitos

Antes de começar, certifique-se de que você tem os seguintes softwares instalados:

- [Python 3.9+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### Passo a Passo

1. **Clone o repositório:**

   ```bash
   git clone <URL_DO_SEU_REPOSITORIO_GIT>
   cd squad-atendimentos-treinamento-cognitivo
   ```
2. **Crie e ative um ambiente virtual:**

   O uso de um ambiente virtual (`venv`) é crucial para isolar as dependências do projeto.

   * **No Windows:**

     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   * **No macOS ou Linux:**

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. **Instale as dependências:**

   Todas as bibliotecas Python necessárias para o projeto estão listadas no arquivo `requirements.txt`.

   ```bash
   pip install -r requirements.txt
   ```
4. **Configure as variáveis de ambiente:**

   As configurações sensíveis (como chaves de API, senhas de banco de dados, etc.) devem ser gerenciadas em um arquivo `.env`.

   ```bash
   # Copie o arquivo de exemplo para criar seu arquivo de configuração local
   cp .env.example .env
   ```

   Em seguida, abra o arquivo `.env` recém-criado e preencha as variáveis com os valores corretos para o seu ambiente.
5. **Execute a aplicação:**

   ```bash
   uvicorn app.main:app --reload
   ```

Pronto! A aplicação deverá estar rodando no seu servidor local.
