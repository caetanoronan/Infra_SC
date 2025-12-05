# 🗺️ Gerador de Mapas Customizados - Infraestrutura SC

Sistema completo para gerar mapas customizados em PNG selecionando camadas de infraestrutura de Santa Catarina.

## 🚀 Funcionalidades

✅ **Seleção de Camadas**
- 🚗 Transportes Terrestres (Rodovias, Ferrovias)
- 🌉 Obras de Arte (Pontes, Túneis, Viadutos)
- ⚓ Marítima e Fluvial (Hidrovias, Dutos, Terminais)
- ✈️ Aviação (Helipontos, Construções Aeroportuárias)
- 🏛️ Limites Político-Administrativos

✅ **Geração de Mapas**
- Visualização em tempo real no navegador
- Mapa interativo com Leaflet
- Zoom e navegação fluida

✅ **Exportação em PNG**
- Nome customizável para o arquivo
- Salva automaticamente em `Mapas_prontos/`
- Timestamp automático no nome

## 📋 Requisitos

- Python 3.8+
- GeoDataFrame com shapefiles BC25 (já configurado)
- Navegador web moderno

## 🔧 Instalação

### 1. Instalar dependências

```bash
cd "C:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Infra_SC"
.\.venv\Scripts\activate
pip install -r requirements_gerador.txt
```

### 2. Executar a aplicação

```bash
python app_gerador_mapas.py
```

### 3. Acessar no navegador

```
http://localhost:5000
```

## 📝 Como Usar

1. **Selecionar Camadas**: Marque as camadas desejadas no painel esquerdo
2. **Nomear Arquivo**: Digite o nome do arquivo (opcional)
3. **Gerar Mapa**: Clique em "Gerar Mapa"
4. **Visualizar**: O mapa aparece na tela
5. **Exportar PNG**: Clique em "Exportar PNG" para salvar em `Mapas_prontos/`

## 📁 Estrutura de Diretórios

```
Infra_SC/
├── app_gerador_mapas.py          # Backend Flask
├── templates/
│   └── gerador_mapas_app.html    # Interface web
├── bc25_sc_shapefile_2020-10-01/ # Dados geográficos
├── Mapas_prontos/                # Mapas exportados (PNG)
└── temp_maps/                     # Mapas temporários (HTML)
```

## 🛠️ Arquitetura

### Backend (Python/Flask)
- **app_gerador_mapas.py**
  - Carrega shapefiles com GeoPandas
  - Otimiza geometrias (simplificação + redução de precisão)
  - Gera mapas Folium
  - API REST para comunicação

### Frontend (HTML/JavaScript)
- **gerador_mapas_app.html**
  - Interface responsiva
  - Comunicação com API via fetch
  - Visualização interativa com Leaflet

## 🔄 Fluxo de Dados

```
Usuario Seleciona Camadas
    ↓
Frontend envia POST /api/gerar-mapa
    ↓
Backend carrega shapefiles + otimiza
    ↓
Folium gera HTML com GeoJSON
    ↓
HTML renderizado no mapa
    ↓
Usuario clica "Exportar PNG"
    ↓
Backend captura screenshot
    ↓
PNG salvo em Mapas_prontos/
```

## 📊 Camadas Disponíveis

### Transportes Terrestres
| Camada | Arquivo Shapefile | Cores |
|--------|-------------------|-------|
| Rodovias Federais | fed_trecho_rodoviario_l.shp | 🔴 Vermelho |
| Rodovias Estaduais | est_trecho_rodoviario_l.shp | 🔵 Azul |
| Ferrovias | fer_trecho_ferrovia_l.shp | 🟣 Roxo |

### Obras de Arte
| Camada | Arquivo Shapefile | Cores |
|--------|-------------------|-------|
| Pontes | bnm_ponte_p.shp | 🟡 Roxo-claro |
| Túneis | bnm_tunel_l.shp | 🟠 Laranja |
| Viadutos | bnm_viaduto_l.shp | 🩷 Rosa |

### Marítima e Fluvial
| Camada | Arquivo Shapefile | Cores |
|--------|-------------------|-------|
| Hidrovias | hhi_trecho_hidrovia_l.shp | 🔵 Azul-escuro |
| Dutos | dut_trecho_duto_l.shp | 🟤 Marrom |
| Terminais | tte_terminal_ponto_a.shp | 🔴 Vermelho |

### Aviação
| Camada | Arquivo Shapefile | Cores |
|--------|-------------------|-------|
| Helipontos | aer_pista_ponto_pouso_p.shp | 🟠 Laranja |
| Construções Aeroportuárias | edf_edif_constr_aeroportuaria_a.shp | 🔵 Azul |

### Limites
| Camada | Arquivo Shapefile | Cores |
|--------|-------------------|-------|
| Limite Estadual | lml_unidade_federacao_a.shp | ⬛ Preto |
| Municípios | lml_municipio_a.shp | ⬜ Cinza |

## 🎨 Personalizações

### Mudar Cores
Editar `COLORS` em `app_gerador_mapas.py`:

```python
COLORS = {
    'rodovias-federais': '#e41a1c',  # Vermelho
    'rodovias-estaduais': '#377eb8',  # Azul
    # ...
}
```

### Mudar Tolerância de Simplificação
Editar `simplificar_geometrias()`:

```python
gdf = simplificar_geometrias(gdf, tolerance=0.001)  # Aumentar para maior simplificação
```

## 🐛 Solução de Problemas

### "Arquivo não encontrado"
✅ Verificar se `bc25_sc_shapefile_2020-10-01/` existe

### "Erro ao carregar camadas"
✅ Verificar se Flask está rodando na porta 5000

### "PNG não foi criado"
✅ Verificar permissões em `Mapas_prontos/`
✅ Verificar espaço em disco

## 📚 Dados

**Fonte:** IBGE - BC25 (2020)  
**Escala:** 1:25.000  
**CRS:** EPSG:4326 (WGS84)  
**Cobertura:** Santa Catarina, Brasil

## 👨‍💻 Autor

Ronan Armando Caetano  
Técnico em Geoprocessamento  
Dezembro 2025

## 📄 Licença

MIT License - Veja LICENSE para detalhes

## 🤝 Contribuindo

Sugestões e melhorias são bem-vindas!

---

**🚀 Pronto para gerar mapas customizados!**
