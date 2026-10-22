# ✦ Sidebar Windows (Dock Vertical)

<p align="center">
  <a href="https://github.com/Rafael-Parola/sidebar-windows/releases/latest">
    <img src="https://img.shields.io/badge/⬇️_Baixar_Instalador_Windows-Release_v1.0.0-6366f1?style=for-the-badge&logo=windows&logoColor=white" alt="Download Sidebar Windows" />
  </a>
</p>

<p align="center">
  <a href="https://github.com/Rafael-Parola/sidebar-windows/releases/latest"><img src="https://img.shields.io/github/v/release/Rafael-Parola/sidebar-windows?color=10b981&label=Vers%C3%A3o%20Est%C3%A1vel" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/Plataforma-Windows_10_%7C_11-0078d4?logo=windows" alt="Plataforma Windows">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
  <a href="LICENSE"><img src="https://img.shields.io/badge/Licen%C3%A7a-GPL_v3-blue" alt="Licença"></a>
</p>

Uma barra lateral ultra-compacta em formato de **Dock Vertical** para Windows, com design minimalista baseado **apenas em ícones**, **auto-ocultamento inteligente (Auto-Hide na borda da tela)**, tooltips informativos e **gerenciamento de início automático de aplicativos**.

---

## 📥 Como Instalar (Recomendado)

Não é necessário ter Python nem nenhuma dependência instalada na sua máquina:

1. Acesse a página de **[Releases Oficiais](https://github.com/Rafael-Parola/sidebar-windows/releases/latest)**.
2. Baixe o arquivo **`Sidebar_Setup_v1.0.0.exe`**.
3. Execute o instalador e siga o assistente.
   - Cria atalhos na Área de Trabalho e Menu Iniciar.
   - Opção de iniciar automaticamente ao ligar o computador.
   - Suas configurações e atalhos ficam salvos com segurança em `%APPDATA%\Sidebar`.

---

## 🎯 Principais Recursos

1. **Apenas Ícones (Sem Poluição Visual)**:
   - A barra exibe exclusivamente os ícones dos seus aplicativos favoritos em um dock vertical de 68px.
   - Ao passar o mouse sobre qualquer ícone, surge um **tooltip flutuante moderno** com o nome, categoria e status do auto-start.
   - Aplicativos configurados para auto-start exibem um discreto **ponto verde (•)**.

2. **Auto-Ocultar Inteligente (Auto-Hide na Borda)**:
   - A barra **recolhe-se automaticamente** ao afastar o mouse.
   - Quando oculta, fica apenas uma linha imperceptível (sensor de borda) no canto da tela.
   - Para reabrir: basta **levar o cursor do mouse até a borda da tela**! Ela desliza instantaneamente.

3. **Início Automático (⚡ Auto-Start)**:
   - **Clique com o botão direito** em qualquer aplicativo para ligar ou desligar o início automático (`✓ Início Automático`).
   - Botão **`⚡` no rodapé da barra**: Dispara imediatamente todos os aplicativos configurados.
   - Na engrenagem **`⚙`**, você pode ativar o **Início com o Windows**, fazendo o Sidebar e seus apps iniciarem ao ligar o computador.

4. **Ícones Customizáveis (Opcional & Seguro)**:
   - O Sidebar extrai automaticamente o ícone original do executável ou atalho.
   - Você também pode escolher qualquer imagem (`.ico`, `.png`, `.jpg`, `.webp`).
   - **Cópia Local Automática**: A imagem é salva localmente, garantindo que scripts externos de limpeza de arquivos nunca quebrem o ícone configurado.

---

## 🎮 Controles e Atalhos Rápidos

| Ação | Onde | O que faz |
| :--- | :--- | :--- |
| **Passar o mouse na borda da tela** | Borda direita (ou esquerda) | A barra surge na tela |
| **Afastar o mouse da barra** | Fora da barra | A barra se recolhe e oculta automaticamente |
| **Passar o mouse no ícone** | Qualquer app | Mostra o tooltip com o nome e status |
| **Clique com botão esquerdo** | Qualquer app | Abre o aplicativo imediatamente |
| **Clique com botão direito** | Qualquer app | Menu de opções (Auto-Start, Editar, Remover) |
| **Botão `+`** | Topo da barra | Adiciona um novo executável ou atalho |
| **Botão `⚡`** | Rodapé da barra | Dispara todos os apps marcados com auto-start |
| **Botão `⚙`** | Rodapé da barra | Configurações (Lado da tela, Boot com Windows, Delays) |

---

## 🛠 Executando a partir do Código-Fonte (Desenvolvedores)

Se você preferir rodar ou contribuir com o código-fonte em Python:

### 1. Clonar o repositório
```bash
git clone https://github.com/Rafael-Parola/sidebar-windows.git
cd sidebar-windows
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Executar o Sidebar
- **Modo Silencioso (Segundo plano)**: Dê um duplo clique em `Sidebar.vbs`
- **Modo Console (Para depuração)**: Dê um duplo clique em `run.bat` ou execute `python main.py`

---

## 📦 Como Compilar o Instalador Localmente

Para gerar seu próprio instalador `.exe` a partir do código:

1. Certifique-se de ter o [Inno Setup 6](https://jrsoftware.org/isdl.php) instalado.
2. Dê um duplo clique no arquivo:
   ```
   build_installer.bat
   ```
3. O script verificará o PyInstaller, compilará o executável e gerará o instalador em:
   ```
   dist_installer\Sidebar_Setup_v1.0.0.exe
   ```

---

## 📄 Licença

Distribuído sob a licença **GPL-3.0**. Consulte [LICENSE](LICENSE) para mais informações.
