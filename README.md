# 🗺️ Mapa de Infraestrutura Logística - Santa Catarina

Um projeto interativo e completo de visualização e análise de infraestrutura logística de Santa Catarina utilizando dados oficiais do IBGE (BC25 - 2020).

## 📊 Visão Geral

Este projeto integra **10.250+ elementos geográficos** em **14 camadas de dados**, apresentando uma análise completa da infraestrutura de transportes em Santa Catarina, incluindo:

- 🛣️ **7.900 Rodovias** (10.840+ km)
- 🚂 **74 Ferrovias** (500+ km)
- ⛵ **223 Infraestruturas Marítimas** (terminais, portos, cais)
- 🌉 **1.622 Obras de Arte** (pontes, viadutos, túneis)
- ✈️ **117 Infraestruturas Aéreas** (helipontos, construções)
- 🌊 **Hidrovias e Dutos** (200+ km)
- 🗺️ **295 Municípios** classificados por porte

## 🎯 Recursos Principais

### Mapa Interativo
- Visualização em tempo real com 14 camadas temáticas
- Controle de visibilidade de camadas
- Pop-ups informativos ao clicar nos elementos
- Zoom e navegação fluida
- Compass (rosa dos ventos) para orientação

### Relatório Estatístico
- **11 abas temáticas** com análise completa
- **5 gráficos interativos** Plotly
- Explicações auto-explicativas
- Modo escuro com contraste WCAG AAA
- Tabelas comparativas e dados detalhados
- Recomendações estratégicas

### Análise de Dados
- Classificação de municípios por porte territorial
- Análise de quilometragem por modalidade
- Distribuição de infraestrutura
- Implicações estratégicas para logística
- Referências IBGE 2020

## 🚀 Como Usar

### Visualizar o Mapa
1. Abra `mapa_infraestrutura_bc25_sc.html` em seu navegador
2. Use o **Controle de Camadas** (canto superior direito) para ativar/desativar dados
3. Clique nos elementos para ver detalhes
4. Use Zoom +/- para navegar

### Visualizar o Relatório
1. Abra `relatorio_infraestrutura.html` em seu navegador
2. Navegue pelas **11 abas** para explorar diferentes aspectos
3. Clique em **🌙 Modo Escuro** para alternar tema
4. Interaja com os gráficos Plotly (zoom, hover, etc.)

## 📁 Estrutura do Projeto

```
Infra_SC/
├── README.md                                    # Este arquivo
├── LICENSE                                      # Licença do projeto
├── .gitignore                                  # Configurações Git
├── mapa_bc25_sc.py                             # Script do mapa
├── relatorio_estatistico.py                    # Script do relatório
├── mapa_infraestrutura_bc25_sc.html           # Mapa interativo
├── relatorio_infraestrutura.html              # Relatório completo
├── chart1_elementos.html                       # Gráfico 1
├── chart2_quilometragem.html                   # Gráfico 2
├── chart3_municipios_porte.html                # Gráfico 3
├── chart4_obras_arte.html                      # Gráfico 4
├── chart5_maritima.html                        # Gráfico 5
└── bc25_sc_shapefile_2020-10-01/              # Dados IBGE BC25
    └── [arquivos .shp, .shx, .dbf, etc.]
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.14+** - Processamento de dados
- **GeoPandas 1.0+** - Operações geográficas
- **Folium** - Mapas interativos
- **Plotly** - Gráficos interativos
- **HTML5 + CSS3 + JavaScript** - Interface web
- **IBGE BC25 2020** - Dados geográficos oficiais

## 📊 Dados Utilizados

**Fonte:** Banco de Dados Geográfico Contínuo (BC25) - IBGE (2020)
- **Escala:** 1:25.000
- **CRS:** EPSG:4674 (SIRGAS 2000) → EPSG:4326 (WGS84)
- **Unidade Federativa:** Santa Catarina, Brasil
- **Publicidade:** Dados públicos do IBGE

### Camadas Incluídas
1. Limite Estadual SC
2. Limites Municipais (classificados por porte)
3. Rodovias Federais
4. Rodovias Estaduais
5. Ferrovias
6. Helipontos
7. Construções Aeroportuárias
8. Terminais/Atracadouros
9. Áreas Portuárias
10. Cais/Molhes
11. Dutos
12. Hidrovias
13. Pontes
14. Túneis
15. Passagens Elevadas/Viadutos

## 📈 Análise Realizada

### Constatações Principais
- ✅ Predominância da malha rodoviária (7.900 rodovias)
- ✅ Complexidade topográfica refletida (1.622 obras de arte)
- ✅ Infraestrutura portuária robusta (223 elementos)
- ✅ Modalidades de transporte complementares
- ✅ Cobertura geográfica equilibrada (295 municípios)

### Implicações Estratégicas
- Planejamento urbano baseado em infraestrutura existente
- Otimização de rotas multimodais
- Competitividade logística regional
- Manutenção preventiva sistematizada
- Desenvolvimento de hubs multimodais

## 🎨 Design e Acessibilidade

- ✅ Interface profissional e intuitiva
- ✅ Modo claro e escuro (alternável)
- ✅ Contraste WCAG AAA (100% legível)
- ✅ Navegação responsiva
- ✅ Totalmente compatível com navegadores modernos

## 📝 Como Contribuir

1. **Fork** este repositório
2. Crie uma **branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. Abra um **Pull Request**

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

Os dados do IBGE BC25 são de **domínio público**.

## 👨‍💻 Autor

**Ronan Armando Caetano**
- Graduado em Ciências Biológicas
- Técnico em Geoprocessamento
- Técnico em Saneamento

## 🙏 Agradecimentos

- **IBGE** - Fornecimento dos dados geográficos oficiais (BC25 2020)
- **GeoPandas** - Operações geográficas em Python
- **Folium** - Visualização de mapas interativos
- **Plotly** - Gráficos interativos e responsivos

## 📞 Contato e Suporte

Para dúvidas, sugestões ou reportar problemas:
- Abra uma **Issue** neste repositório
- Verifique a seção **Discussions**

## 🔗 Links Úteis

- [IBGE - Dados Geográficos](https://www.ibge.gov.br/)
- [GeoPandas Documentation](https://geopandas.org/)
- [Folium Documentation](https://folium.readthedocs.io/)
- [Plotly Documentation](https://plotly.com/python/)

---

**Versão:** 1.0.0  
**Última Atualização:** Dezembro 2025  
**Status:** ✅ Completo e Funcional

⭐ Se este projeto foi útil, considere dar uma estrela! ⭐

## 🚀 Deploy Online

**Instruções completas:** [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)

### Deploy Rápido (Render)
1. Crie conta: https://dashboard.render.com
2. New Web Service → Conecte repo `caetanoronan/Infra_SC`
3. Runtime: Python 3 | Start: `playwright install --with-deps chromium && python app_gerador_mapas_final.py`
4. Env vars: `HOST=0.0.0.0`, `SHAPEFILE_URL=https://github.com/caetanoronan/Infra_SC/releases/download/v1.0.0-data/bc25_sc_shapefiles.zip`
5. Deploy! (5-8 min)

**Shapefiles:** Baixados automaticamente da [Release v1.0.0-data](https://github.com/caetanoronan/Infra_SC/releases/tag/v1.0.0-data)

## 🌐 Acesso Online

**GitHub Pages:** [https://caetanoronan.github.io/Infra_SC/](https://caetanoronan.github.io/Infra_SC/)

### Links Diretos:
- 📄 [Página Inicial](https://caetanoronan.github.io/Infra_SC/index.html)
- 🗺️ [Mapa Completo Interativo](https://caetanoronan.github.io/Infra_SC/mapa_infraestrutura_dinamico.html)
- 📊 [Relatório Estatístico](https://caetanoronan.github.io/Infra_SC/relatorio_infraestrutura.html)
- 🎨 [Gerador de Mapas Customizados](https://infra-sc.onrender.com) ⭐ **NOVO!**

> **💡 Nota:** O mapa carrega 15 camadas GeoJSON otimizadas (total ~30 MB) dinamicamente para contornar o limite de 100 MB do GitHub.

---

## 🔄 Replicar para Outros Estados/Países

Este projeto foi desenvolvido para ser **100% replicável** em outros estados brasileiros ou países! 🌍

### 📦 O que está disponível no repositório:
- ✅ Todo o código-fonte (Python, HTML, CSS, JavaScript)
- ✅ Scripts de geração de mapas e relatórios
- ✅ Configurações de deploy (Dockerfile, requirements.txt)
- ✅ Documentação completa (README, DEPLOY_GUIDE)
- ✅ Template do gerador customizado com exportação PNG

### 🛠️ Como adaptar para outro local:

#### 1️⃣ Obter dados geográficos do local desejado

**Para outros estados brasileiros:**
- Baixar shapefiles BC25 do IBGE: https://www.ibge.gov.br/geociencias/downloads-geociencias.html
- Escolher o estado desejado (ex: Rio Grande do Sul, Paraná, etc.)

**Para outros países:**
- OpenStreetMap: https://download.geofabrik.de/
- Dados governamentais locais
- Natural Earth: https://www.naturalearthdata.com/

#### 2️⃣ Ajustar configurações no código

Editar `app_gerador_mapas_final.py` (ou scripts de mapa):

```python
# Ajustar caminho dos shapefiles
SHAPEFILE_DIR = BASE_DIR / "bc25_rs_shapefile_2020-10-01"  # Exemplo: RS

# Ajustar coordenadas centrais do mapa
mapa = folium.Map(
    location=[-30.0, -51.2],  # Ex: Porto Alegre, RS
    zoom_start=7,
    ...
)

# Ajustar mapeamento de camadas (se nomes de arquivos mudarem)
LAYER_MAPPING = {
    'rodovias-federais': ('rod_via_deslocamento_l.shp', ...),
    # Verificar nomes exatos dos arquivos .shp do novo local
}
```

#### 3️⃣ Preparar dados para deploy

```bash
# Compactar shapefiles
python prepare_shapefiles.py

# Subir ZIP na GitHub Release do seu fork
# Atualizar URL no Render: SHAPEFILE_URL=https://github.com/SEU_USUARIO/SEU_REPO/releases/download/...
```

#### 4️⃣ Deploy

Seguir o mesmo processo do [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md):
- Deploy no Render (ou outra plataforma)
- Configurar variáveis de ambiente
- Publicar no GitHub Pages

### 🌎 Exemplos de adaptação:

| Local | Ajustes Principais |
|-------|-------------------|
| **Outros Estados BR** | Apenas trocar shapefiles e coordenadas centrais |
| **Portugal** | Adaptar nomes de colunas (ex: "jurisdição" → "jurisdiction") |
| **EUA/Europa** | Usar dados OpenStreetMap; ajustar estrutura de dados |
| **América Latina** | Similar ao Brasil; verificar formato dos shapefiles locais |

### 💡 Dicas para adaptação:

1. **Mantenha a estrutura**: Os scripts são genéricos e funcionam com qualquer shapefile
2. **Verifique colunas**: Use `geopandas` para inspecionar nomes de colunas dos novos dados
3. **Teste localmente**: Rode `python app_gerador_mapas_final.py` antes de fazer deploy
4. **Documente mudanças**: Atualize README com informações do novo local

### 📚 Recursos úteis:

- **IBGE Geociências**: https://www.ibge.gov.br/geociencias.html
- **GeoPandas Docs**: https://geopandas.org/
- **Folium Docs**: https://python-visualization.github.io/folium/
- **OpenStreetMap**: https://wiki.openstreetmap.org/

---
