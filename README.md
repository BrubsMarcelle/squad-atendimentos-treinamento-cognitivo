# Sistema de Treinamento Cognitivo para Atendimentos

Este projeto é uma aplicação destinada a fornecer treinamento cognitivo para squads de atendimento, com o objetivo de melhorar a performance, a agilidade e a qualidade do serviço prestado aos clientes.

## 🎯 Objetivo da Aplicação

O sistema visa oferecer uma plataforma com exercícios e simulações que estimulam habilidades cognitivas essenciais para profissionais de atendimento, tais como:

-   Memória de curto prazo
-   Atenção seletiva
-   Resolução de problemas sob pressão
-   Raciocínio lógico

Através de um acompanhamento de progresso, a ferramenta permite que gestores e colaboradores identifiquem pontos de melhoria e fortaleçam suas competências.

---

## 🚀 Como Rodar o Projeto Localmente

Siga os passos abaixo para configurar e executar a aplicação em seu ambiente de desenvolvimento.

### Pré-requisitos

Antes de começar, certifique-se de que você tem os seguintes softwares instalados:

-   [Python 3.9+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)

### Passo a Passo

1.  **Clone o repositório:**

    ```bash
    git clone <URL_DO_SEU_REPOSITORIO_GIT>
    cd squad-atendimentos-treinamento-cognitivo
    ```

2.  **Crie e ative um ambiente virtual:**

    O uso de um ambiente virtual (`venv`) é crucial para isolar as dependências do projeto.

    *   **No Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

    *   **No macOS ou Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instale as dependências:**

    Todas as bibliotecas Python necessárias para o projeto estão listadas no arquivo `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```
    *(Observação: Se este arquivo ainda não existir, você pode criá-lo com `pip freeze > requirements.txt` após instalar as dependências manualmente.)*

4.  **Configure as variáveis de ambiente:**

    As configurações sensíveis (como chaves de API, senhas de banco de dados, etc.) devem ser gerenciadas em um arquivo `.env`.

    ```bash
    # Copie o arquivo de exemplo para criar seu arquivo de configuração local
    cp .env.example .env
    ```
    Em seguida, abra o arquivo `.env` recém-criado e preencha as variáveis com os valores corretos para o seu ambiente.

5.  **Execute a aplicação:**

    ```bash
    # O comando pode variar. Use o que for apropriado para o seu projeto (ex: flask run, python manage.py runserver, etc.)
    python main.py
    ```

Pronto! A aplicação deverá estar rodando no seu servidor local.