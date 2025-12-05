"""
Script para servir arquivos comprimidos (.gz) como HTML
Descompacta automaticamente quando acessado via GitHub Pages
"""

import gzip
import json
from pathlib import Path

def decompress_and_serve():
    """
    Cria versões descompactadas dos arquivos .gz
    para serem servidas pelo GitHub Pages
    """
    
    gz_files = [
        ('mapa_infraestrutura_bc25_sc.min.html.gz', 'mapa_infraestrutura_bc25_sc.html'),
        ('relatorio_infraestrutura.min.html.gz', 'relatorio_infraestrutura.html'),
    ]
    
    for gz_file, output_file in gz_files:
        gz_path = Path(gz_file)
        if gz_path.exists():
            print(f"📦 Descompactando {gz_file}...")
            with gzip.open(gz_path, 'rb') as f_in:
                content = f_in.read()
            
            with open(output_file, 'wb') as f_out:
                f_out.write(content)
            
            output_size = Path(output_file).stat().st_size / (1024 * 1024)
            print(f"✅ {output_file} criado ({output_size:.2f} MB)")
        else:
            print(f"❌ {gz_file} não encontrado")

if __name__ == "__main__":
    print("=" * 70)
    print("📦 DESCOMPRESSOR DE ARQUIVOS - Para GitHub Pages")
    print("=" * 70)
    decompress_and_serve()
    print("\n✅ Arquivos prontos para GitHub Pages!")
