#!/usr/bin/env python3
"""
Git Manager - Automatización de respaldo en GitHub
TMP AI Assistant - QuickBooks Automation

Autor: Alfredo
Fecha: Enero 2026
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import json

# =================================================================
# CONFIGURACIÓN
# =================================================================

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Archivos y carpetas sensibles que NO deben estar en Git
SENSITIVE_FILES = [
    '.env',
    '.env.local',
    '.env.production',
    'chart_of_accounts.json',
    'token_usage.csv',
    'credentials.json',
]

SENSITIVE_FOLDERS = [
    'Backup',
    'Bank Reconciliation',
    'Pending bills',
    'Processed bills',
    'Test',
    '__pycache__',
    '.venv',
    'venv',
]

# Configuración del repositorio
REPO_URL = "https://github.com/alfredojfp/qbo-ai-assistant.git"
BRANCH = "main"

# =================================================================
# UTILIDADES
# =================================================================

def print_header(text):
    """Imprime encabezado con formato"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def run_command(command, capture_output=True, check=True):
    """Ejecuta comando en shell y retorna resultado"""
    try:
        if capture_output:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=check)
            return None
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Error ejecutando: {command}")
            print_error(f"Mensaje: {e.stderr}")
            return None
        return e.stderr

def get_project_stats():
    """Obtiene estadísticas del proyecto"""
    stats = {}
    
    # Contar archivos Python
    py_files = list(Path('.').rglob('*.py'))
    stats['python_files'] = len([f for f in py_files if '.venv' not in str(f)])
    
    # Contar líneas de código
    total_lines = 0
    for py_file in py_files:
        if '.venv' not in str(py_file):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                pass
    stats['total_lines'] = total_lines
    
    # Contar módulos de autonomía
    autonomia_path = Path('autonomia')
    if autonomia_path.exists():
        stats['autonomia_modules'] = len(list(autonomia_path.glob('*.py'))) - 1  # -1 por __init__.py
    else:
        stats['autonomia_modules'] = 0
    
    return stats

# =================================================================
# FUNCIONES PRINCIPALES
# =================================================================

def check_sensitive_files():
    """Verifica que no haya archivos sensibles sin proteger"""
    print_header("VERIFICACIÓN DE SEGURIDAD")
    
    issues_found = False
    
    # Verificar archivos sensibles
    print_info("Verificando archivos sensibles...")
    for file in SENSITIVE_FILES:
        if os.path.exists(file):
            # Verificar si está en .gitignore
            with open('.gitignore', 'r') as f:
                gitignore_content = f.read()
                if file not in gitignore_content:
                    print_warning(f"Archivo sensible NO protegido: {file}")
                    issues_found = True
                else:
                    print_success(f"Protegido: {file}")
    
    # Verificar carpetas sensibles
    print_info("\nVerificando carpetas sensibles...")
    for folder in SENSITIVE_FOLDERS:
        if os.path.exists(folder):
            with open('.gitignore', 'r') as f:
                gitignore_content = f.read()
                if folder not in gitignore_content and f"{folder}/" not in gitignore_content:
                    print_warning(f"Carpeta sensible NO protegida: {folder}/")
                    issues_found = True
                else:
                    print_success(f"Protegida: {folder}/")
    
    # Verificar git status
    print_info("\nVerificando archivos en staging...")
    status_output = run_command("git status --short")
    
    if status_output:
        for line in status_output.split('\n'):
            for sensitive in SENSITIVE_FILES + [f"{f}/" for f in SENSITIVE_FOLDERS]:
                if sensitive in line:
                    print_error(f"ARCHIVO SENSIBLE EN STAGING: {line}")
                    issues_found = True
    
    if not issues_found:
        print_success("\n✓ No se detectaron problemas de seguridad")
        return True
    else:
        print_error("\n✗ Se encontraron problemas de seguridad")
        return False

def show_status():
    """Muestra estado del repositorio"""
    print_header("ESTADO DEL REPOSITORIO")
    
    # Branch actual
    branch = run_command("git branch --show-current")
    print_info(f"Branch actual: {branch}")
    
    # Último commit
    last_commit = run_command("git log -1 --pretty=format:'%h - %s (%cr)' 2>/dev/null", check=False)
    if last_commit:
        print_info(f"Último commit: {last_commit}")
    
    # Archivos modificados
    print("\n" + Colors.BOLD + "Archivos modificados:" + Colors.END)
    status = run_command("git status --short")
    if status:
        print(status)
    else:
        print_success("No hay cambios pendientes")
    
    # Estadísticas del proyecto
    print("\n" + Colors.BOLD + "Estadísticas del proyecto:" + Colors.END)
    stats = get_project_stats()
    print_info(f"Archivos Python: {stats['python_files']}")
    print_info(f"Líneas de código: {stats['total_lines']:,}")
    print_info(f"Módulos de autonomía: {stats['autonomia_modules']}")

def commit_and_push(message=None, auto=False):
    """Realiza commit y push automático"""
    print_header("COMMIT Y PUSH A GITHUB")
    
    # Verificar seguridad primero
    if not check_sensitive_files():
        print_error("\nAbortando por problemas de seguridad")
        response = input("\n¿Continuar de todas formas? (sí/no): ").lower()
        if response not in ['sí', 'si', 's', 'yes', 'y']:
            return False
    
    # Ver archivos que se agregarán
    print_info("\nArchivos que se agregarán:")
    status = run_command("git status --short")
    if not status:
        print_warning("No hay cambios para commitear")
        return False
    print(status)
    
    # Confirmar si no es automático
    if not auto:
        response = input(f"\n{Colors.YELLOW}¿Continuar con el commit? (sí/no): {Colors.END}").lower()
        if response not in ['sí', 'si', 's', 'yes', 'y']:
            print_info("Operación cancelada")
            return False
    
    # Agregar archivos
    print_info("\nAgregando archivos...")
    run_command("git add .", capture_output=False)
    print_success("Archivos agregados")
    
    # Generar mensaje si no se proporcionó
    if not message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        stats = get_project_stats()
        message = f"Update: {timestamp} - {stats['python_files']} archivos Python, {stats['total_lines']:,} líneas"
    
    # Commit
    print_info(f"\nCreando commit: {message}")
    run_command(f'git commit -m "{message}"', capture_output=False)
    print_success("Commit creado")
    
    # Push
    print_info(f"\nSubiendo a GitHub ({BRANCH})...")
    result = run_command(f"git push origin {BRANCH}", capture_output=False, check=False)
    
    if result is None:
        print_success("✓ Push completado exitosamente")
        print_info(f"Repositorio: {REPO_URL}")
        return True
    else:
        print_error("Error en el push")
        return False

def create_backup_branch():
    """Crea una rama de backup con timestamp"""
    print_header("CREAR RAMA DE BACKUP")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    branch_name = f"backup_{timestamp}"
    
    print_info(f"Creando rama: {branch_name}")
    
    # Crear rama
    run_command(f"git checkout -b {branch_name}", capture_output=False)
    print_success(f"Rama {branch_name} creada")
    
    # Commit si hay cambios
    status = run_command("git status --short")
    if status:
        run_command("git add .", capture_output=False)
        run_command(f'git commit -m "Backup automático {timestamp}"', capture_output=False)
        print_success("Cambios commiteados en rama de backup")
    
    # Push de la rama
    print_info("Subiendo rama a GitHub...")
    run_command(f"git push origin {branch_name}", capture_output=False)
    print_success(f"Rama {branch_name} respaldada en GitHub")
    
    # Volver a main
    run_command(f"git checkout {BRANCH}", capture_output=False)
    print_info(f"De vuelta en {BRANCH}")

def generate_report():
    """Genera reporte del repositorio"""
    print_header("REPORTE DEL REPOSITORIO")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "branch": run_command("git branch --show-current"),
        "last_commit": run_command("git log -1 --pretty=format:'%H'", check=False),
        "total_commits": run_command("git rev-list --count HEAD", check=False),
        "contributors": run_command("git shortlog -sn --all", check=False),
        "stats": get_project_stats(),
        "remote": REPO_URL
    }
    
    # Guardar reporte JSON
    report_file = f"git_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print_success(f"Reporte generado: {report_file}")
    
    # Mostrar resumen
    print("\n" + Colors.BOLD + "Resumen:" + Colors.END)
    print_info(f"Branch: {report['branch']}")
    print_info(f"Total commits: {report['total_commits']}")
    print_info(f"Archivos Python: {report['stats']['python_files']}")
    print_info(f"Líneas de código: {report['stats']['total_lines']:,}")
    print_info(f"Módulos de autonomía: {report['stats']['autonomia_modules']}")
    
    return report_file

def setup_git():
    """Configura Git inicial si no está configurado"""
    print_header("CONFIGURACIÓN INICIAL DE GIT")
    
    # Verificar si ya está inicializado
    if os.path.exists('.git'):
        print_warning("Repositorio ya inicializado")
        return
    
    # Inicializar Git
    print_info("Inicializando repositorio Git...")
    run_command("git init", capture_output=False)
    print_success("Git inicializado")
    
    # Configurar usuario
    print_info("\nConfigurando usuario Git...")
    run_command('git config user.name "Alfredo"', capture_output=False)
    run_command('git config user.email "ajparra4@gmail.com"', capture_output=False)
    print_success("Usuario configurado")
    
    # Agregar remote
    print_info(f"\nAgregando repositorio remoto...")
    run_command(f"git remote add origin {REPO_URL}", capture_output=False, check=False)
    print_success("Repositorio remoto agregado")
    
    # Renombrar rama a main
    run_command(f"git branch -M {BRANCH}", capture_output=False, check=False)
    print_success(f"Rama renombrada a {BRANCH}")

def show_menu():
    """Muestra menú interactivo"""
    print_header("GIT MANAGER - TMP AI ASSISTANT")
    
    print(f"{Colors.BOLD}Opciones disponibles:{Colors.END}\n")
    print(f"  {Colors.CYAN}1.{Colors.END} Ver estado del repositorio")
    print(f"  {Colors.CYAN}2.{Colors.END} Verificar seguridad (archivos sensibles)")
    print(f"  {Colors.CYAN}3.{Colors.END} Commit y Push a GitHub")
    print(f"  {Colors.CYAN}4.{Colors.END} Commit y Push automático (sin confirmación)")
    print(f"  {Colors.CYAN}5.{Colors.END} Crear rama de backup")
    print(f"  {Colors.CYAN}6.{Colors.END} Generar reporte del repositorio")
    print(f"  {Colors.CYAN}7.{Colors.END} Configuración inicial de Git")
    print(f"  {Colors.CYAN}8.{Colors.END} Salir")
    print()

# =================================================================
# MAIN
# =================================================================

def main():
    """Función principal"""
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('main.py'):
        print_error("No estás en el directorio del proyecto 'Qbo Scripts'")
        print_info("Navega a: ~/Escritorio/Qbo Scripts")
        sys.exit(1)
    
    # Modo comando directo
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            show_status()
        elif command == "check":
            check_sensitive_files()
        elif command == "push":
            message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
            commit_and_push(message=message)
        elif command == "auto":
            message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
            commit_and_push(message=message, auto=True)
        elif command == "backup":
            create_backup_branch()
        elif command == "report":
            generate_report()
        elif command == "setup":
            setup_git()
        else:
            print_error(f"Comando desconocido: {command}")
            print_info("Comandos disponibles: status, check, push, auto, backup, report, setup")
        
        return
    
    # Modo interactivo
    while True:
        show_menu()
        
        try:
            choice = input(f"{Colors.YELLOW}Selecciona una opción (1-8): {Colors.END}").strip()
            
            if choice == '1':
                show_status()
            elif choice == '2':
                check_sensitive_files()
            elif choice == '3':
                message = input(f"\n{Colors.YELLOW}Mensaje del commit (Enter para auto): {Colors.END}").strip()
                commit_and_push(message=message if message else None)
            elif choice == '4':
                message = input(f"\n{Colors.YELLOW}Mensaje del commit (Enter para auto): {Colors.END}").strip()
                commit_and_push(message=message if message else None, auto=True)
            elif choice == '5':
                create_backup_branch()
            elif choice == '6':
                generate_report()
            elif choice == '7':
                setup_git()
            elif choice == '8':
                print_info("\n¡Hasta luego!")
                break
            else:
                print_warning("Opción inválida")
            
            input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.END}")
            
        except KeyboardInterrupt:
            print_info("\n\n¡Hasta luego!")
            break
        except Exception as e:
            print_error(f"\nError: {e}")
            input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.END}")

if __name__ == "__main__":
    main()
