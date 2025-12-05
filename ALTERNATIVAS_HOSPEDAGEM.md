# 🌐 Alternativas para Hospedar Arquivos HTML Grandes

## ❌ Problema Atual
GitHub Pages com Git LFS não funciona bem para arquivos HTML grandes (> 50MB). O GitHub retorna um pointer do LFS em vez do arquivo real.

## ✅ Soluções Recomendadas

### Opção 1: Vercel (⭐ Recomendado - GRÁTIS)
**Vantagens:**
- Sem limite de tamanho de arquivo
- Deploy automático via Git
- Muito rápido (CDN global)
- HTTPS automático
- Grátis para projetos pessoais

**Passos:**
1. Acesse: https://vercel.com
2. Clique em "Continue with GitHub"
3. Autorize e selecione o repositório `Infra_SC`
4. Clique em "Deploy"
5. Em poucos minutos, seu site estará em:
   - `https://infra-sc.vercel.app/` (ou seu domínio personalizado)

**Links após deploy:**
- Mapa: `https://infra-sc.vercel.app/mapa_infraestrutura_bc25_sc.html`
- Relatório: `https://infra-sc.vercel.app/relatorio_infraestrutura.html`
- Index: `https://infra-sc.vercel.app/`

---

### Opção 2: Netlify (⭐ GRÁTIS)
**Vantagens:**
- Similar ao Vercel
- Sem limite de tamanho
- Interface intuitiva

**Passos:**
1. Acesse: https://www.netlify.com
2. Clique em "Connect from Git"
3. Selecione GitHub e autorize
4. Escolha o repositório `Infra_SC`
5. Configure e clique em "Deploy site"

**Links após deploy:**
- Site: `https://seu-site.netlify.app/`

---

### Opção 3: GitHub Releases (Para Arquivos Individuais)
Se quiser manter no GitHub, pode fazer upload de releases:

**Passos:**
1. No repositório, vá em: Releases > Draft a new release
2. Crie uma release (v1.0.0)
3. Faça upload dos arquivos HTML grandes
4. Links dos downloads estarão disponíveis

---

### Opção 4: Firebase Hosting (Google - GRÁTIS)
**Vantagens:**
- Armazenamento generoso
- Deploy fácil via CLI
- Hospedagem rápida

**Passos:**
1. Crie conta em: https://firebase.google.com
2. Instale Firebase CLI: `npm install -g firebase-tools`
3. Execute: `firebase init hosting`
4. Faça upload: `firebase deploy`

---

## 📊 Comparação Rápida

| Plataforma | Tamanho Máximo | Setup | Velocidade | Custo |
|-----------|---------|-------|-----------|-------|
| GitHub Pages | 100MB (sem LFS) | Fácil | Bom | Grátis |
| Vercel | Ilimitado | Muito Fácil | Excelente | Grátis |
| Netlify | Ilimitado | Muito Fácil | Excelente | Grátis |
| Firebase | Generoso | Médio | Bom | Grátis |

---

## 🚀 Recomendação Final

**Use VERCEL** - É literalmente 3 cliques e deploy automático! 

Quando você fizer `git push` para a branch main, Vercel automaticamente redeploy o site com as mudanças.

---

## 📝 Como Atualizar depois de Deploy

Qualquer uma das plataformas acima:

```powershell
# Faça suas mudanças
git add .
git commit -m "Descrição das mudanças"
git push origin main

# Site atualiza automaticamente em alguns segundos
```

---

## 🔗 Links de Deploy

Após escolher uma plataforma, atualizaremos o `index.html` para apontar para o novo domínio.

**Para começar agora, qual plataforma você prefere?**
- ✨ Vercel (recomendado)
- 🌐 Netlify
- 🔥 Firebase
- 📦 GitHub Releases

