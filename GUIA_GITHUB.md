# 📚 Guia Completo: GitHub e GitHub Pages

## 1️⃣ Configuração Inicial do Git

### Instalar Git
Se ainda não tem Git instalado:
- **Windows:** https://git-scm.com/download/win
- **Mac:** `brew install git`
- **Linux:** `sudo apt-get install git`

### Configurar Git (primeira vez)
```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

## 2️⃣ Criar Repositório no GitHub

1. Acesse https://github.com/new
2. Nome: `Infra_SC`
3. Descrição: "Mapa e análise interativa de infraestrutura logística de Santa Catarina"
4. Visibilidade: **Public** (para GitHub Pages funcionar)
5. Clique em "Create repository"

## 3️⃣ Enviar Projeto para GitHub

### Via Terminal PowerShell

```powershell
# Navegar para o diretório do projeto
cd "C:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Infra_SC"

# Inicializar repositório Git
git init

# Adicionar todos os arquivos
git add .

# Primeiro commit
git commit -m "Inicial: Mapa e relatório de infraestrutura logística SC"

# Adicionar origem remota (copie a URL do seu repositório GitHub)
git remote add origin https://github.com/SEU-USUARIO/Infra_SC.git

# Enviar para GitHub (main branch)
git branch -M main
git push -u origin main
```

## 4️⃣ Ativar GitHub Pages

1. No repositório GitHub, clique em **Settings**
2. Na esquerda, clique em **Pages**
3. Em "Source", selecione:
   - Branch: `main`
   - Diretório: `/ (root)`
4. Clique em "Save"

Aguarde 1-2 minutos e seu site estará disponível em:
```
https://SEU-USUARIO.github.io/Infra_SC/
```

## 5️⃣ Acessar os Arquivos

### Mapa Interativo
https://SEU-USUARIO.github.io/Infra_SC/mapa_infraestrutura_bc25_sc.html

### Relatório Estatístico
https://SEU-USUARIO.github.io/Infra_SC/relatorio_infraestrutura.html

### Página Inicial (README)
https://SEU-USUARIO.github.io/Infra_SC/

## 6️⃣ Fazer Atualizações Futuras

Sempre que quiser enviar mudanças:

```powershell
# Ir para o diretório
cd "C:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Infra_SC"

# Ver status
git status

# Adicionar arquivos
git add .

# Fazer commit
git commit -m "Descrição da mudança"

# Enviar para GitHub
git push origin main
```

## 7️⃣ Compartilhar o Projeto

### Links para Compartilhar

**Repositório GitHub:**
```
https://github.com/SEU-USUARIO/Infra_SC
```

**Mapa Público:**
```
https://SEU-USUARIO.github.io/Infra_SC/mapa_infraestrutura_bc25_sc.html
```

**Relatório Público:**
```
https://SEU-USUARIO.github.io/Infra_SC/relatorio_infraestrutura.html
```

### Compartilhar em Redes

- 📧 Email: Copie os links
- 🔗 LinkedIn: Compartilhe o repositório
- 📱 WhatsApp: Cole os links
- 🐦 Twitter: "Confira meu projeto de mapa logístico de SC! 🗺️"

## 8️⃣ Dicas e Troubleshooting

### Site não aparece?
- Verifique se o repositório é **PUBLIC**
- Aguarde 2-3 minutos após ativar Pages
- Limpe o cache do navegador (Ctrl+Shift+Delete)

### Erro ao fazer push?
```powershell
# Se der erro de autenticação, gere um token:
# 1. GitHub → Settings → Developer settings → Personal access tokens
# 2. Generate new token (classic)
# 3. Selecione "repo" scope
# 4. Copie o token
# 5. Use como senha ao fazer push
```

### Atualizar depois?
```powershell
git add .
git commit -m "Atualização: descrição"
git push origin main
# Aguarde 1-2 minutos para o site atualizar
```

## 9️⃣ Próximos Passos Opcionais

- ✅ Adicionar badge de status no README
- ✅ Criar releases no GitHub
- ✅ Adicionar wiki com documentação
- ✅ Configurar domínio personalizado (custom domain)
- ✅ Habilitar discussions para feedback

## 🔟 Recursos Úteis

- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Hello World](https://guides.github.com/activities/hello-world/)
- [Markdown Guide](https://www.markdownguide.org/)

---

**Pronto! Seu projeto estará público e acessível para o mundo! 🚀**
