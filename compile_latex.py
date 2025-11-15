"""
Script para compilar el documento LaTeX
"""

import subprocess
import os
import sys


def compile_latex():
    """
    Compila el documento LaTeX usando pdflatex.
    """
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    main_tex = 'main.tex'
    
    print("=" * 70)
    print("Compilando documento LaTeX...")
    print("=" * 70)
    print()
    
    # Cambiar al directorio de documentos
    original_dir = os.getcwd()
    os.chdir(docs_dir)
    
    try:
        # Primera compilación
        print("Primera compilación...")
        result1 = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', main_tex],
            capture_output=True,
            text=True
        )
        
        if result1.returncode != 0:
            print("Error en la primera compilación:")
            print(result1.stdout)
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
            print(result2.stdout)
            return False
        
        print()
        print("=" * 70)
        print("✓ Documento compilado exitosamente")
        print("=" * 70)
        print(f"Archivo PDF: {os.path.join(docs_dir, 'main.pdf')}")
        print()
        
        # Limpiar archivos auxiliares
        print("Limpiando archivos auxiliares...")
        aux_extensions = ['.aux', '.log', '.out', '.toc']
        for ext in aux_extensions:
            aux_file = 'main' + ext
            if os.path.exists(aux_file):
                os.remove(aux_file)
                print(f"  Eliminado: {aux_file}")
        
        return True
        
    except FileNotFoundError:
        print("Error: pdflatex no está instalado o no está en el PATH")
        print("Por favor, instala una distribución de LaTeX como:")
        print("  - MacTeX (macOS)")
        print("  - TeX Live (Linux)")
        print("  - MiKTeX (Windows)")
        return False
    
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False
    
    finally:
        # Volver al directorio original
        os.chdir(original_dir)


if __name__ == "__main__":
    success = compile_latex()
    sys.exit(0 if success else 1)
