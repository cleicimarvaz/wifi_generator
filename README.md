# Gerador de Placas Wi-Fi

Este é uma aplicação desktop desenvolvida em Python para automatizar a criação de placas de conexão Wi-Fi. O sistema gera um QR Code configurável e exporta um arquivo PDF vetorial pronto para impressão (formato A4), seguindo a identidade visual da Delta Telecom.

## 🚀 Funcionalidades

* **Geração de QR Code:** Suporte para redes WPA/WPA2, WEP e Abertas.
* **Exportação PDF:** Gera um arquivo PDF vetorizado com design limpo, moldura e logo da empresa.
* **Exportação PNG:** Opção para salvar apenas o QR Code como imagem.
* **Impressão Direta:** Integração com o sistema de impressão do Windows (permite escolher a impressora).
* **Visualização:** Botão para visualizar o PDF antes de imprimir ou salvar.
* **Interface Amigável:** GUI construída com Tkinter, incluindo recurso para visualizar/esconder a senha digitada.
* **Portátil:** Compilável para um único arquivo `.exe` com recursos embutidos.

## 🛠️ Tecnologias Utilizadas

* [Python 3](https://www.python.org/)
* **Tkinter:** Interface Gráfica.
* **ReportLab:** Geração de PDFs vetoriais.
* **Segno:** Geração de códigos QR.
* **Pillow (PIL):** Manipulação de imagens.
* **PyWin32:** Controle de impressão no Windows.
* **PyInstaller:** Compilação do executável.

## 📦 Como rodar o projeto localmente

### Pré-requisitos

Certifique-se de ter o Python instalado. É recomendado usar um ambiente virtual (`venv`).

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/NOME_DO_REPO.git](https://github.com/SEU_USUARIO/NOME_DO_REPO.git)
    cd NOME_DO_REPO
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuração da Imagem:**
    Certifique-se de que o arquivo de logo esteja na raiz do projeto com o nome exato:
    * `image_1.png`

4.  **Execute a aplicação:**
    ```bash
    python gerador_wifi.py
    ```

## ⚙️ Compilando o Executável (.exe)

Para gerar um arquivo executável que funciona em computadores sem Python instalado, utilizamos o **PyInstaller**.

1.  Instale as dependências.
2.  Execute o comando de build (incluindo o logo dentro do executável):
    ```bash
    pyinstaller --noconsole --onefile --add-data "image_1.png;." gerador_wifi.py
    ```
3.  O arquivo `.exe` será gerado na pasta `dist`.

## 📂 Estrutura do Projeto

📁 Pasta_do_Projeto/
│
├── 📄 gerador_wifi.py       <-- O código Python
├── 🖼️ image_1.png           <-- O logo (O nome DEVE ser esse)
├── 📄 requirements.txt      <-- Arquivo com a lista de bibliotecas
├── 📄 README.md             <-- Arquivo de documentação
└── 📁 dist/                 <-- (Esta pasta aparece só depois de gerar o .exe)
    └── 🚀 gerador_wifi.exe  <-- O seu programa pronto para enviar/usar
    
## 📝 Licença

Este projeto foi desenvolvido para fins educacionais e de uso interno.
