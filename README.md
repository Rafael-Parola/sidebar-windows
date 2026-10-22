# ✦ Sidebar Windows (Dock Vertical)

Uma barra lateral ultra-compacta em formato de **Dock Vertical** para Windows, com design minimalista baseado **apenas em ícones**, **auto-ocultamento automático (Auto-Hide na borda da tela)**, tooltips informativos e **gerenciamento de início automático**.

---

## 🎯 Como Funciona

1. **Apenas Ícones (Sem Poluição Visual)**:
   - A barra exibe exclusivamente os ícones dos aplicativos em um dock vertical elegante de 62px.
   - Ao passar o mouse sobre qualquer ícone, um **tooltip flutuante moderno** surge ao lado exibindo o **Nome do Aplicativo**, categoria e se está com o **Auto-Start ativo**.
   - Ícones configurados para início automático exibem um discreto **ponto verde (•)** no canto inferior direito.

2. **Auto-Ocultar Automático (Auto-Hide Inteligente)**:
   - A barra **oculta-se sozinha** sempre que você afasta o mouse dela.
   - Quando oculta, fica apenas uma linha imperceptível (sensor de borda) no canto da tela.
   - Para reabrir a barra: basta **levar o cursor do mouse até a borda da tela**! Ela desliza instantaneamente para frente.

3. **Início Automático (⚡ Auto-Start)**:
   - **Clique com o botão direito** no ícone de qualquer aplicativo para ativar ou desativar o início automático (`✓ Início Automático`).
   - Botão **`⚡` no rodapé da barra**: Dispara imediatamente todos os aplicativos configurados para auto-start.
   - Na engrenagem **`⚙`**, você pode ativar o **Início com o Windows**, fazendo com que a barra e seus aplicativos abram sozinhos ao ligar o PC.

4. **Ícones Customizáveis (Opcional & Seguro)**:
   - Por padrão, o Sidebar extrai o ícone nativo real do executável/atalho.
   - Ao adicionar ou editar um app, você pode clicar em **`🖼 Escolher...`** (ou no quadradinho do ícone) e selecionar qualquer imagem (`.ico`, `.png`, `.jpg`, `.webp`).
   - **Cópia Local Automática**: A imagem é automaticamente copiada e convertida para a pasta interna `assets/custom_icons/` do Sidebar, garantindo que scripts externos de organização ou limpeza de arquivos nunca quebrem ou percam o ícone!
   - Um botão **`✕`** permite voltar para o ícone padrão automático a qualquer momento.

---

## 🛠 Como Executar

### 1. Modo Silencioso (Recomendado para o dia a dia):
Dê um duplo clique no arquivo:
```
Sidebar.vbs
```
*(Executa em segundo plano com `pythonw.exe`, sem abrir nenhuma janela de prompt de comando).*

### 2. Modo com Console (Para testes):
Dê um duplo clique no arquivo:
```
run.bat
```

---

## 📦 Instalador Oficial para Windows

Para gerar um instalador profissional `.exe` (que permite instalar em qualquer computador sem precisar ter Python instalado):

1. Dê um duplo clique no arquivo **`build_installer.bat`**.
2. O instalador será gerado na pasta:
   ```
   dist_installer\Sidebar_Setup_v1.0.0.exe
   ```
3. O instalador configura atalhos na Área de Trabalho, Menu Iniciar, inicialização automática com o Windows e desinstalador no Painel de Controle. As configurações e ícones customizados ficam salvos de forma segura em `%APPDATA%\Sidebar`.

---

## 🎮 Controles Rápidos da Barra

| Ação | Onde | O que faz |
| :--- | :--- | :--- |
| **Passar o mouse sobre a borda da tela** | Borda direita (ou esquerda) | A barra desliza e surge na tela |
| **Afastar o mouse da barra** | Fora da barra | A barra se recolhe e oculta automaticamente |
| **Passar o mouse no ícone** | Qualquer app | Mostra o tooltip com o nome e status |
| **Clique com botão esquerdo** | Qualquer app | Abre o aplicativo imediatamente |
| **Clique com botão direito** | Qualquer app | Menu de opções (Auto-Start, Editar, Remover) |
| **Botão `+`** | Topo da barra | Adiciona um novo executável ou atalho |
| **Botão `⚡`** | Rodapé da barra | Dispara todos os apps marcados com auto-start |
| **Botão `⚙`** | Rodapé da barra | Abre as configurações (Lado da tela, Boot com Windows, Delays) |
