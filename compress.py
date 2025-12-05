"""
Compressor Prático de Mapas HTML
Remove dados desnecessários e minifica o HTML
"""

import re
import gzip
import json
import os
from pathlib import Path

def minify_html(html_content):
    """Minifica HTML removendo espaços e comentários"""
    # Remove comentários HTML
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Remove espaços múltiplos (mantém 1)
    html_content = re.sub(r'\s+', ' ', html_content)
    
    # Remove espaços antes de >
    html_content = re.sub(r'\s+>', '>', html_content)
    
    # Remove espaços depois de <
    html_content = re.sub(r'<\s+', '<', html_content)
    
    return html_content

def remove_redundant_data(html_content):
    """Remove dados redundantes do HTML"""
    # Remove atributos de estilo inline redundantes
    html_content = re.sub(r'\s+style="[^"]*"', '', html_content)
    
    # Remove data attributes desnecessários
    html_content = re.sub(r'\s+data-[^=]*="[^"]*"', '', html_content)
    
    return html_content

def compress_html_file(input_file, output_file=None):
    """
    Comprime arquivo HTML
    """
    if not os.path.exists(input_file):
        print(f"❌ Arquivo não encontrado: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_file.replace('.html', '.min.html')
    
    # Obter tamanho original
    original_size = os.path.getsize(input_file) / (1024 * 1024)
    print(f"\n📦 Comprimindo: {input_file}")
    print(f"   Tamanho original: {original_size:.2f} MB")
    
    # Ler arquivo
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print("   🔧 Minificando HTML...")
    content = minify_html(content)
    
    print("   🔧 Removendo dados redundantes...")
    content = remove_redundant_data(content)
    
    # Salvar versão minificada
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    minified_size = os.path.getsize(output_file) / (1024 * 1024)
    minify_ratio = (1 - minified_size / original_size) * 100
    
    print(f"   ✅ Minificado: {minified_size:.2f} MB ({minify_ratio:.1f}% redução)")
    
    # Comprimir com gzip
    gzip_file = output_file + '.gz'
    print(f"   🔧 Aplicando Gzip...")
    
    with open(output_file, 'rb') as f_in:
        with gzip.open(gzip_file, 'wb', compresslevel=9) as f_out:
            f_out.write(f_in.read())
    
    gzip_size = os.path.getsize(gzip_file) / (1024 * 1024)
    gzip_ratio = (1 - gzip_size / original_size) * 100
    
    print(f"   ✅ Gzip comprimido: {gzip_size:.2f} MB ({gzip_ratio:.1f}% redução)")
    
    print(f"\n📊 RESULTADOS:")
    print(f"   Original:        {original_size:.2f} MB")
    print(f"   Minificado:      {minified_size:.2f} MB ({minify_ratio:.1f}%)")
    print(f"   Gzip:            {gzip_size:.2f} MB ({gzip_ratio:.1f}%)")
    print(f"\n✅ Arquivos gerados:")
    print(f"   {output_file}")
    print(f"   {gzip_file}")
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("🗜️  COMPRESSOR DE MAPAS HTML")
    print("=" * 70)
    
    # Comprimir o mapa principal
    compress_html_file("mapa_infraestrutura_bc25_sc.html")
    
    # Comprimir os relatórios
    compress_html_file("relatorio_infraestrutura.html")
    
    # Comprimir os gráficos
    for chart in range(1, 6):
        compress_html_file(f"chart{chart}_*.html" if chart == 1 else f"chart{chart}_*.html")
    
    print("\n" + "=" * 70)
    print("✨ PRÓXIMOS PASSOS")
    print("=" * 70)
    print("""
1. Verifique os arquivos .min.html gerados
2. Teste-os no navegador
3. Se tudo funcionar, suba para GitHub:
   
   git add *.min.html*
   git commit -m "Add: Versões comprimidas dos mapas e relatórios"
   git push origin main

4. Atualize o index.html para apontar para as versões .min.html

🎯 Meta: Reduzir de 136 MB para ~20-30 MB!
""")
