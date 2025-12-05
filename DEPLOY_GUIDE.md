# 🚀 Guia de Deploy - Render

Este guia mostra como publicar o app online no Render (plano gratuito disponível).

## 📋 Pré-requisitos

- Conta no GitHub (já tem ✓)
- Conta no Render: https://dashboard.render.com/register
- Repositório já está pronto com:
  - `app_gerador_mapas_final.py`
  - `requirements.txt`
  - `Dockerfile`
  - Shapefiles na Release v1.0.0-data

## 🎯 Passo a Passo

### 1. Criar Conta no Render

1. Acesse: https://dashboard.render.com/register
2. Faça login com sua conta GitHub
3. Autorize o Render a acessar seus repositórios

### 2. Criar Web Service

1. No dashboard do Render, clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório **caetanoronan/Infra_SC**
3. Se não aparecer, clique em "Configure account" e autorize acesso

### 3. Configurar o Service

Preencha os campos:

#### Informações Básicas
- **Name:** `infra-sc-mapas` (ou outro nome)
- **Region:** `Oregon (US West)` (mais próximo e estável)
- **Branch:** `main`
- **Root Directory:** (deixe vazio)

#### Build & Deploy
- **Runtime:** `Python 3`
- **Build Command:** (deixe vazio)
- **Start Command:** 
  ```bash
  playwright install --with-deps chromium && python app_gerador_mapas_final.py
  ```

#### Variáveis de Ambiente (Environment Variables)

Clique em **"Add Environment Variable"** e adicione:

| Key | Value |
|-----|-------|
| `HOST` | `0.0.0.0` |
| `SHAPEFILE_URL` | `https://github.com/caetanoronan/Infra_SC/releases/download/v1.0.0-data/bc25_sc_shapefiles.zip` |

#### Plano (Instance Type)
- **Free** (512 MB RAM) - para teste
- **Starter** ($7/mês, 512 MB RAM) - produção (não hiberna)

### 4. Deploy

1. Clique em **"Create Web Service"**
2. O Render vai:
   - Clonar o repositório
   - Instalar dependências do `requirements.txt`
   - Instalar Playwright + Chromium (~300 MB)
   - Baixar e extrair shapefiles (~183 MB download, 342 MB descompactado)
   - Iniciar o servidor Flask

**⏱️ Tempo estimado:** 5-8 minutos no primeiro deploy

### 5. Acessar o App

Quando o deploy terminar (status "Live"), você verá a URL pública:
```
https://infra-sc-mapas.onrender.com
```

Clique e teste o gerador de mapas!

## 🔧 Configurações Importantes

### Auto-Deploy
- Por padrão, o Render faz deploy automático a cada push no `main`
- Para desativar: Settings → Build & Deploy → Auto-Deploy = OFF

### Logs
- Acesse: Dashboard → seu service → Logs
- Útil para debug se algo der errado

### Custom Domain (Opcional)
- Settings → Custom Domain
- Adicione seu próprio domínio se tiver

## ⚠️ Limitações do Plano Free

- **Hibernação:** App "dorme" após 15 min de inatividade
- **Cold Start:** Primeira requisição após hibernar leva 30-60s
- **Bandwidth:** 100 GB/mês
- **Build Time:** 500 horas/mês

**Solução:** Upgrade para Starter ($7/mês) para app sempre ativo.

## 🐛 Troubleshooting

### Deploy falhou

**Erro:** "Build failed"
- Verifique os logs
- Comum: timeout ao instalar Chromium (aumenta automaticamente no retry)

**Erro:** "Download shapefiles failed"
- Verifique se `SHAPEFILE_URL` está correta
- Teste a URL manualmente no navegador

### App não carrega mapas

1. Verifique logs: procure por `[OK] Shapefiles extraídos`
2. Se não aparecer, verifique `SHAPEFILE_URL`
3. Reinicie o service: Manual Deploy → Clear build cache & deploy

### PNG export não funciona

- Playwright pode levar tempo para instalar
- Verifique logs: procure por `chromium installed`
- Se falhar, adicione mais memória (upgrade para Starter)

## 📊 Monitoramento

### Metrics
- Dashboard → Metrics
- CPU, Memory, Request count

### Health Check
- Adicione: `/api/status`
- Render verifica se app está rodando

## 🔄 Atualizações

Para atualizar o app:
1. Faça push das mudanças no GitHub
2. Render faz deploy automático
3. Ou: Manual Deploy → Deploy latest commit

## 💰 Custos Estimados

| Plano | Preço | RAM | Uptime | Ideal para |
|-------|-------|-----|--------|-----------|
| Free | $0 | 512 MB | Hiberna após 15min | Testes/demo |
| Starter | $7/mês | 512 MB | 24/7 | Produção básica |
| Standard | $25/mês | 2 GB | 24/7 | Uso intenso |

## 🎉 Pronto!

Seu app está online e acessível de qualquer lugar:
- Gerador de mapas customizados
- Exportação para PNG
- Dados oficiais IBGE BC25

**URL do seu app:** https://infra-sc-mapas.onrender.com (ou o nome que escolheu)

---

**Dúvidas?** Abra uma issue no GitHub: https://github.com/caetanoronan/Infra_SC/issues
