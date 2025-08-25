# Anexa Fácil 📄✨

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white)

Uma aplicação web inteligente para unificar boletos e comprovantes de pagamento em um único documento PDF, de forma rápida e profissional.

**[➡️ Clique aqui para ver a demonstração ao vivo](https://anexa-facil.vercel.app/)**

---

## 🎯 Sobre o Projeto

O "Anexa Fácil" nasceu da necessidade de otimizar uma tarefa manual e repetitiva: a de juntar um boleto em PDF com seu respectivo comprovante de pagamento em imagem. O processo, geralmente feito em editores de texto, era lento e pouco prático.

Esta aplicação resolve o problema com uma interface web moderna e um backend poderoso, automatizando todo o processo em segundos.

---

## ✨ Principais Funcionalidades

* **Unificação de Arquivos:** Combina um arquivo PDF e um arquivo de imagem em um único documento PDF.
* **Nome de Arquivo Inteligente (OCR):** Utiliza OCR (Reconhecimento Óptico de Caracteres) para ler o nome do pagador e a data de vencimento do boleto, gerando um nome de arquivo padronizado e organizado.
* **Interface Moderna:** Design responsivo, com tema escuro, criado com React e Tailwind CSS.
* **Pré-visualização de Imagem:** O usuário pode ver uma miniatura do comprovante antes de enviar.
* **Otimização no Frontend:** Comprime as imagens no navegador antes do upload para um processamento mais rápido e eficiente.
* **Tratamento de Erros:** Valida os tipos de arquivo no backend e exibe mensagens de erro claras para o usuário.

---

## 🛠️ Tecnologias Utilizadas

#### **Frontend**
* **React.js:** Biblioteca principal para a construção da interface.
* **Tailwind CSS:** Para estilização rápida e moderna.
* **browser-image-compression:** Para otimização das imagens no lado do cliente.

#### **Backend**
* **Python 3.9:** Linguagem principal da API.
* **Flask:** Micro-framework para criar a API.
* **Pillow:** Para manipulação e colagem de imagens.
* **pdf2image:** Para converter as páginas do PDF em imagens.
* **pytesseract:** Wrapper Python para o motor de OCR Tesseract.

#### **Infraestrutura e Deploy**
* **Vercel:** Para a hospedagem do frontend e do backend (serverless functions).
* **Git & GitHub:** Para versionamento de código e fluxo de CI/CD com a Vercel.

---

## 🚀 Como Rodar Localmente

Para rodar este projeto na sua máquina, siga os passos abaixo.

### Pré-requisitos
* **Node.js** (v18 ou superior)
* **Python** (v3.9 ou superior) e `pip`
* **Git**
* **Dependências de Sistema (Linux/Debian):**
  ```bash
  sudo apt-get update
  sudo apt-get install poppler-utils tesseract-ocr tesseract-ocr-por
  ```

### Instalação e Execução

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/janailsonf-a/anexa-facil.git](https://github.com/janailsonf-a/anexa-facil.git)
    cd anexa-facil
    ```

2.  **Configure e rode o Backend (Terminal 1):**
    ```bash
    # Crie e ative o ambiente virtual
    python3 -m venv .venv
    source .venv/bin/activate
    
    # Instale as dependências Python
    pip install -r api/requirements.txt
    
    # Rode o servidor Flask
    flask --app api/process run
    ```

3.  **Configure e rode o Frontend (Terminal 2):**
    ```bash
    # Instale as dependências do Node.js
    npm install
    
    # Rode o servidor de desenvolvimento do React
    npm start
    ```
4.  Abra seu navegador e acesse `http://localhost:3000`.

---

## 👤 Autor

**Janailson Firmino**
* GitHub: [@janailsonf-a](https://github.com/janailsonf-a)

---

Projeto desenvolvido como parte de um processo de aprendizado contínuo, com a ajuda do **Parceiro de Programação**.
