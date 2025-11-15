#!/usr/bin/env python3
"""
Script para compilar el documento LaTeX modularizado
"""

import subprocess
import os
import sys


def compile_latex():
    """Compila el documento LaTeX modularizado."""
    
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    main_tex = 'main.tex'
    
    print("=" * 80)
    print("Compilando documento LaTeX modularizado...")
    print("=" * 80)
    print()
    
    # Cambiar al directorio de documentos
    original_dir = os.getcwd()
    os.chdir(docs_dir)
    
    try:
        # Verificar que main.tex existe
        if not os.path.exists(main_tex):
            print(f"Error: {main_tex} no encontrado")
            return False
        
        # Primera compilación
        print("Primera compilación...")
        result1 = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', main_tex],
            capture_output=True,
            text=True
        )
        
        if result1.returncode != 0:
            print("Error en la primera compilación:")
            print(result1.stdout[-500:])  # Últimas 500 líneas
            return False
        
        # Segunda compilación para referencias
        print("Segunda compilación (para referencias)...")
        result2 = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', main_tex],
            capture_output=True,
            text=True
        )
        
        if result2.returncode != 0:
            print("Error en la segunda compilación:")
            print(result2.stdout[-500:])
            return False
        
        print()
        print("=" * 80)
        print("✓ Documento compilado exitosamente")
        print("=" * 80)
        
        pdf_file = 'main.pdf'
        if os.path.exists(pdf_file):
            size_kb = os.path.getsize(pdf_file) / 1024
            print(f"PDF generado: {pdf_file} ({size_kb:.1f} KB)")
        
        # Limpiar archivos auxiliares
        print("\nLimpiando archivos auxiliares...")
        aux_extensions = ['.aux', '.log', '.out', '.toc', '.synctex.gz']
        removed = 0
        for ext in aux_extensions:
            aux_file = 'main' + ext
            if os.path.exists(aux_file):
                os.remove(aux_file)
                removed += 1
        print(f"Eliminados {removed} archivos auxiliares")
        
        return True
        
    except FileNotFoundError:
        print("Error: pdflatex no está instalado")
        print("Instala LaTeX: brew install --cask mactex (macOS)")
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    success = compile_latex()
    sys.exit(0 if success else 1)
