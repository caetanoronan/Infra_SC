import geopandas as gpd
import folium
from pathlib import Path
import pandas as pd

# Caminho base dos shapefiles BC25
BASE_DIR = Path(r"C:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Infra_SC\bc25_sc_shapefile_2020-10-01")

# --- Carregar camadas ---
print("📥 Carregando shapefiles BC25...")
uf = gpd.read_file(BASE_DIR / "lml_unidade_federacao_a.shp").to_crs("EPSG:4326")
municipios = gpd.read_file(BASE_DIR / "lml_municipio_a.shp").to_crs("EPSG:4326")
# Calcular area e classificar porte (pequeno/medio/grande) por tercis de area
muni_merc = municipios.to_crs(3857)
municipios["area_km2"] = muni_merc.geometry.area / 1e6
q1, q2 = municipios["area_km2"].quantile([0.33, 0.66])

def _porte(area):
    if area <= q1:
        return "Pequeno"
    if area <= q2:
        return "Medio"
    return "Grande"

municipios["porte_area"] = municipios["area_km2"].apply(_porte)
porte_counts = municipios["porte_area"].value_counts()
roads = gpd.read_file(BASE_DIR / "rod_via_deslocamento_l.shp").to_crs("EPSG:4326")
roads_main = roads[roads["jurisdicao"].isin(["Federal", "Estadual/Distrital"])]
roads_fed = roads[roads["jurisdicao"] == "Federal"]
roads_est = roads[roads["jurisdicao"] == "Estadual/Distrital"]
ferrovias = gpd.read_file(BASE_DIR / "fer_trecho_ferroviario_l.shp").to_crs("EPSG:4326")
aerodromos = gpd.read_file(BASE_DIR / "aer_pista_ponto_pouso_p.shp").to_crs("EPSG:4326")
helipontos = aerodromos[aerodromos["tipopista"].str.contains("Heliponto", case=False, na=False)]
# Construções aeroportuárias (terminais, hangares, etc.)
construcoes_aero = gpd.read_file(BASE_DIR / "edf_edif_constr_aeroportuaria_p.shp").to_crs("EPSG:4326")
terminais = gpd.read_file(BASE_DIR / "hdv_atracadouro_terminal_p.shp").to_crs("EPSG:4326")
# Portos em áreas (maiores)
terminais_area = gpd.read_file(BASE_DIR / "hdv_atracadouro_terminal_a.shp").to_crs("EPSG:4326")
# Portos em linhas (cais, molhes)
terminais_linha = gpd.read_file(BASE_DIR / "hdv_atracadouro_terminal_l.shp").to_crs("EPSG:4326")
# Infra adicional para escoamento
dutos = gpd.read_file(BASE_DIR / "dut_trecho_duto_l.shp").to_crs("EPSG:4326")
hidrovias = gpd.read_file(BASE_DIR / "hdv_trecho_hidroviario_l.shp").to_crs("EPSG:4326")
pontes = gpd.read_file(BASE_DIR / "tra_ponte_l.shp").to_crs("EPSG:4326")
tuneis = gpd.read_file(BASE_DIR / "tra_tunel_l.shp").to_crs("EPSG:4326")
viadutos = gpd.read_file(BASE_DIR / "tra_passagem_elevada_viaduto_l.shp").to_crs("EPSG:4326")

print(f"   ✓ Rodovias (fed/est): {len(roads_main)}")
print(f"   ✓ Limite estadual: {len(uf)} | Municípios: {len(municipios)}")
print(f"     • Federais: {len(roads_fed)} | Estaduais: {len(roads_est)}")
print(f"     • Porte munic. (Peq/Med/Grd): {porte_counts.get('Pequeno',0)}/{porte_counts.get('Medio',0)}/{porte_counts.get('Grande',0)}")
print(f"   ✓ Ferrovias: {len(ferrovias)}")
print(f"   ✓ Helipontos: {len(helipontos)}")
print(f"   ✓ Construções aeroportuárias: {len(construcoes_aero)}")
print(f"   ✓ Terminais portuários: {len(terminais)} | Áreas portuárias: {len(terminais_area)} | Linhas (cais): {len(terminais_linha)}")
print(f"   ✓ Hidrovias: {len(hidrovias)}")
print(f"   ✓ Dutos: {len(dutos)}")
print(f"   ✓ Pontes: {len(pontes)} | Túneis: {len(tuneis)} | Viadutos: {len(viadutos)}")

# --- Mapa base ---
mapa = folium.Map(
    location=[-27.5, -49.5],
    zoom_start=7,
    tiles="CartoDB positron",
    min_zoom=5,
    max_zoom=12,
)

# Todos os painéis em uma única tag HTML consolidada
ui_html = """
<div id="map-ui-container" style="font-family: Arial, sans-serif;">
    <!-- Titulo fixo no topo do mapa -->
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000; background: rgba(255,255,255,0.92); padding: 8px 14px; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.15); font-size: 16px; font-weight: 600; color: #1f2933; text-align: center;">
        Mapa de Infraestrutura Logistica - Santa Catarina<br>
        <span style="font-size: 12px; font-weight: 500; color: #374151;">Autor: Ronan Armando Caetano · Graduado em Ciências Biológicas · Técnico em Geoprocessamento · Técnico em Saneamento</span>
    </div>

    <!-- Rosa dos ventos (canto superior esquerdo) -->
    <div style="position: fixed; top: 70px; left: 12px; z-index: 1000;">
        <div style="position: relative; width: 60px; height: 60px; border: 2px solid #333; border-radius: 50%; background: rgba(255,255,255,0.92); box-shadow: 0 2px 6px rgba(0,0,0,0.15); display: flex; align-items: center; justify-content: center; font-weight: 700; color: #333;">
            N
            <div style="position: absolute; top: 6px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 7px solid transparent; border-right: 7px solid transparent; border-bottom: 14px solid #d62728;"></div>
        </div>
    </div>

    <!-- Painel de Informações das Camadas (canto inferior esquerdo) -->
    <div style="position: fixed; bottom: 12px; left: 12px; z-index: 1000; max-width: 340px; font-size: 13px;">
        <div id="info-toggle" style="cursor: pointer; background: #ffffff; color: #1f2933; padding: 8px 10px; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.15); display: inline-flex; align-items: center; gap: 6px; font-weight: 600;">
            <span>ℹ️</span><span>Informacoes das camadas</span>
        </div>
        <div id="info-panel" style="display: none; margin-top: 8px; background: rgba(255,255,255,0.96); color: #1f2933; padding: 10px 12px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); line-height: 1.35;">
            <div style="font-weight: 600; margin-bottom: 6px;">Legenda/Descricao</div>
            <ul style="padding-left: 18px; margin: 0;">
                <li>Rodovias federais/estaduais separadas em camadas.</li>
                <li>Ferrovias, hidrovias e dutos como linhas dedicadas.</li>
                <li>Helipontos e construções aeroportuárias (terminais, hangares) como pontos.</li>
                <li>Limites municipais (porte por area) em camada dedicada; limite estadual sempre visivel.</li>
                <li>Pontes, tuneis e viadutos como camadas independentes.</li>
            </ul>
            <div style="margin-top: 8px; font-size: 12px; color: #4a5568;">Use o controle de camadas (canto superior direito) para alternar a visibilidade.</div>
        </div>
    </div>
</div>

<script>
(function(){
    // Toggle Info Panel
    const infoToggle = document.getElementById('info-toggle');
    const infoPanel = document.getElementById('info-panel');
    if (infoToggle && infoPanel) {
        infoToggle.addEventListener('click', function(){
            infoPanel.style.display = infoPanel.style.display === 'none' ? 'block' : 'none';
        });
    }
})();
</script>
"""
mapa.get_root().html.add_child(folium.Element(ui_html))

# Limite estadual (sempre visível)
folium.GeoJson(
    uf,
    name="🧭 Limite Estadual SC",
    style_function=lambda x: {"color": "#000000", "weight": 2.5, "fillOpacity": 0},
    highlight_function=lambda x: {"color": "#ff0000", "weight": 3},
    tooltip=folium.GeoJsonTooltip(fields=["nome", "sigla"], aliases=["UF:", "Sigla:"])
).add_to(mapa)

# Limite municipal por porte (area)
folium.GeoJson(
    municipios,
    name="🗺️ Limites Municipais",
    style_function=lambda x: {
        # BuGn (3 classes)
        "color": {"Pequeno": "#e5f5f9", "Medio": "#99d8c9", "Grande": "#2ca25f"}.get(x["properties"].get("porte_area"), "#666666"),
        "fillColor": {"Pequeno": "#e5f5f9", "Medio": "#99d8c9", "Grande": "#2ca25f"}.get(x["properties"].get("porte_area"), "#f0f0f0"),
        "weight": 1.1,
        "fillOpacity": 0.18,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nome", "geocodigo", "porte_area", "area_km2"],
        aliases=["Municipio", "IBGE", "Porte (area)", "Area km2"],
        localize=True,
        labels=True,
        sticky=True,
    ),
    show=False,
).add_to(mapa)

# Rodovias Federais
folium.GeoJson(
    roads_fed,
    name="🟥 Rodovias Federais",
    style_function=lambda x: {"color": "#d73027", "weight": 2.2, "opacity": 0.9},
    tooltip=folium.GeoJsonTooltip(
        fields=["jurisdicao", "revestimen", "operaciona"],
        aliases=["Jurisd.", "Revestimento", "Operacional"],
        localize=True,
    ),
    show=False,
).add_to(mapa)

# Rodovias Estaduais
folium.GeoJson(
    roads_est,
    name="🟦 Rodovias Estaduais",
    style_function=lambda x: {"color": "#4575b4", "weight": 2.0, "opacity": 0.85},
    tooltip=folium.GeoJsonTooltip(
        fields=["jurisdicao", "revestimen", "operaciona"],
        aliases=["Jurisd.", "Revestimento", "Operacional"],
        localize=True,
    ),
    show=False,
).add_to(mapa)

# Ferrovias
folium.GeoJson(
    ferrovias,
    name="🚂 Ferrovias",
    style_function=lambda x: {"color": "#7b3294", "weight": 2.3, "opacity": 0.9},
    tooltip=folium.GeoJsonTooltip(
        fields=["nome", "tipotrecho", "bitola", "eletrifica"],
        aliases=["Nome", "Tipo", "Bitola", "Eletrificada"],
        localize=True,
    ),
    show=False,
).add_to(mapa)

# Helipontos
if len(helipontos) > 0:
    fg_heli = folium.FeatureGroup(name="🚁 Helipontos", show=False)
    for _, row in helipontos.iterrows():
        tooltip = row.get("nome") or "Heliponto"
        popup = folium.Popup(
            f"<b>{row.get('nome','')}</b><br>Tipo: {row.get('tipopista','')}<br>Uso: {row.get('usopista','')}<br>Operacional: {row.get('operaciona','')}",
            max_width=280,
        )
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,
            color="#f46d43",
            fill=True,
            fill_opacity=0.85,
            popup=popup,
            tooltip=tooltip,
        ).add_to(fg_heli)
    fg_heli.add_to(mapa)

# Construções aeroportuárias (terminais, hangares, etc.)
if len(construcoes_aero) > 0:
    fg_constr_aer = folium.FeatureGroup(name="🏢 Construções Aeroportuárias", show=False)
    for _, row in construcoes_aero.iterrows():
        tooltip = row.get("nome") or "Construção Aeroportuária"
        popup = folium.Popup(
            f"<b>{row.get('nome','')}</b><br>Município: {row.get('municipio','')}<br>Operacional: {row.get('operaciona','')}<br>Situação: {row.get('situacaofi','')}",
            max_width=300,
        )
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,
            color="#3288bd",
            fill=True,
            fill_opacity=0.75,
            popup=popup,
            tooltip=tooltip,
        ).add_to(fg_constr_aer)
    fg_constr_aer.add_to(mapa)

# Terminais / atracadouros
fg_term = folium.FeatureGroup(name="⚓ Terminais/Atracadouros", show=False)
for _, row in terminais.iterrows():
    tipo = row.get("tipoatraca") or "Desconhecido"
    adm = row.get("administra") or "Não informado"
    oper = row.get("operaciona") or "Não informado"
    apt = row.get("aptidaoope") or "Não informado"
    situ = row.get("situacaofi") or "Não informado"
    nome = row.get("nome") or f"Terminal ({tipo})"
    tooltip = nome
    popup = folium.Popup(
        f"<b>{nome}</b><br>Tipo: {tipo}<br>Adm.: {adm}<br>Oper.: {oper}<br>Apt.: {apt}<br>Situação: {situ}",
        max_width=260,
    )
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        color="red",
        fill=True,
        fill_opacity=0.85,
        popup=popup,
        tooltip=tooltip,
    ).add_to(fg_term)
fg_term.add_to(mapa)

# Áreas portuárias (converter para pontos com buffer visual)
if len(terminais_area) > 0:
    fg_area_port = folium.FeatureGroup(name="🏭 Áreas Portuárias", show=False)
    for _, row in terminais_area.iterrows():
        tipo = row.get("tipoatraca") or "Desconhecido"
        oper = row.get("operaciona") or "Não informado"
        nome = row.get("nome") or f"Área Portuária ({tipo})"
        tooltip = nome
        popup = folium.Popup(
            f"<b>{nome}</b><br>Tipo: {tipo}<br>Operacional: {oper}",
            max_width=300,
        )
        # Converter polígono em ponto (centróide) com raio maior
        centroid = row.geometry.centroid
        folium.CircleMarker(
            location=[centroid.y, centroid.x],
            radius=12,
            color="#e41a1c",
            fill=True,
            fill_color="#e41a1c",
            fill_opacity=0.6,
            weight=2.5,
            popup=popup,
            tooltip=tooltip,
        ).add_to(fg_area_port)
    fg_area_port.add_to(mapa)

# Linhas de cais/molhes portuários (converter para pontos)
if len(terminais_linha) > 0:
    fg_cais = folium.FeatureGroup(name="⚓ Cais/Molhes", show=False)
    for _, row in terminais_linha.iterrows():
        tipo = row.get("tipoatraca") or "Desconhecido"
        oper = row.get("operaciona") or "Não informado"
        situ = row.get("situacaofi") or "Não informado"
        tooltip = f"{tipo}"
        popup = folium.Popup(
            f"<b>Cais/Molhe ({tipo})</b><br>Operacional: {oper}<br>Situação: {situ}",
            max_width=280,
        )
        # Converter linha em ponto (centróide)
        centroid = row.geometry.centroid
        folium.CircleMarker(
            location=[centroid.y, centroid.x],
            radius=8,
            color="#4daf4a",
            fill=True,
            fill_color="#4daf4a",
            fill_opacity=0.7,
            weight=2,
            popup=popup,
            tooltip=tooltip,
        ).add_to(fg_cais)
    fg_cais.add_to(mapa)

# Dutos (linhas)
folium.GeoJson(
    dutos,
    name="⛽ Dutos (óleo/gás)",
    style_function=lambda x: {"color": "#a6611a", "weight": 2.6, "opacity": 0.9, "dashArray": "6,4"},
    tooltip=folium.GeoJsonTooltip(
        fields=["nome", "mattransp", "setor", "operaciona" if "operaciona" in dutos.columns else "tipotrecho"],
        aliases=["Nome", "Material", "Setor", "Operacional/Tipo"],
        localize=True,
    ),
    show=False,
).add_to(mapa)

# Hidrovias (linhas)
folium.GeoJson(
    hidrovias,
    name="🛳️ Hidrovias",
    style_function=lambda x: {"color": "#2c7fb8", "weight": 3.2, "opacity": 0.85},
    tooltip=folium.GeoJsonTooltip(
        fields=["operaciona", "situacaofi", "regime", "caladomaxs"],
        aliases=["Operacional", "Situação", "Regime", "Calado máx"],
        localize=True,
    ),
    show=False,
).add_to(mapa)

# Pontes
folium.GeoJson(
    pontes,
    name="🌉 Pontes",
    style_function=lambda x: {"color": "#8073ac", "weight": 2, "opacity": 0.9},
    tooltip=folium.GeoJsonTooltip(
        fields=["nome", "modaluso", "operaciona", "situacaofi"],
        aliases=["Nome", "Modal", "Operacional", "Situação"],
        localize=True,
    ),
    show=False,
).add_to(mapa)

# Túneis
folium.GeoJson(
    tuneis,
    name="🚇 Túneis",
    style_function=lambda x: {"color": "#e08214", "weight": 2.4, "opacity": 0.9, "dashArray": "4,4"},
    tooltip=folium.GeoJsonTooltip(
        fields=["nome", "modaluso", "operaciona", "situacaofi"],
        aliases=["Nome", "Modal", "Operacional", "Situação"],
        localize=True,
    ),
    show=False,
).add_to(mapa)

# Viadutos / passagens elevadas
folium.GeoJson(
    viadutos,
    name="🛤️ Passagens Elevadas",
    style_function=lambda x: {"color": "#d01c8b", "weight": 2.6, "opacity": 0.95},
    tooltip=folium.GeoJsonTooltip(
        fields=["nome", "modaluso", "operaciona", "situacaofi"],
        aliases=["Nome", "Modal", "Operacional", "Situação"],
        localize=True,
    ),
    show=False,
).add_to(mapa)

# Controle de camadas
folium.LayerControl(position="topright", collapsed=False).add_to(mapa)

# Salvar
output = "mapa_infraestrutura_bc25_sc.html"
mapa.save(output)
print(f"✅ Mapa gerado: {output}")
