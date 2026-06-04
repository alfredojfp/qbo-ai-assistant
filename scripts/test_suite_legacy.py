#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SUITE COMPREHENSIVO - TMP AI Assistant
Verifica todas las funcionalidades y herramientas
"""

import os
import sys
import json
from datetime import datetime
from colorama import init, Fore, Style

# Inicializar colorama para colores en terminal
init(autoreset=True)

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []

    def test(self, name, function, *args, **kwargs):
        """Ejecuta un test y registra resultado"""
        print(f"\n{'='*70}")
        print(f"🧪 TEST: {name}")
        print(f"{'='*70}")

        try:
            result = function(*args, **kwargs)
            if result.get('success', True):
                self.passed += 1
                print(f"{Fore.GREEN}✅ PASSED{Style.RESET_ALL}")
                self.results.append({'test': name, 'status': 'PASSED', 'details': result})
            else:
                self.failed += 1
                print(f"{Fore.RED}❌ FAILED: {result.get('error', 'Unknown')}{Style.RESET_ALL}")
                self.results.append({'test': name, 'status': 'FAILED', 'error': result.get('error')})
        except Exception as e:
            self.failed += 1
            print(f"{Fore.RED}❌ EXCEPTION: {str(e)}{Style.RESET_ALL}")
            self.results.append({'test': name, 'status': 'EXCEPTION', 'error': str(e)})

    def warning(self, message):
        """Registra una advertencia"""
        self.warnings += 1
        print(f"{Fore.YELLOW}⚠️  WARNING: {message}{Style.RESET_ALL}")

    def summary(self):
        """Muestra resumen final"""
        total = self.passed + self.failed
        print(f"\n\n{'='*70}")
        print(f"📊 RESUMEN DE TESTS")
        print(f"{'='*70}")
        print(f"Total tests:    {total}")
        print(f"{Fore.GREEN}✅ Passed:      {self.passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Failed:      {self.failed}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  Warnings:    {self.warnings}{Style.RESET_ALL}")
        print(f"Success rate:   {(self.passed/total*100) if total > 0 else 0:.1f}%")
        print(f"{'='*70}")

        # Guardar resultados
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        with open('test_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': total,
                    'passed': self.passed,
                    'failed': self.failed,
                    'warnings': self.warnings
                },
                'results': self.results
            }, f, indent=2, cls=DateTimeEncoder)
        print(f"\n📄 Resultados guardados en: test_results.json")

# Importar módulos del sistema
try:
    from main import (
        # Funciones core
        load_chart_of_accounts,
        search_customer,
        search_vendor,
        find_account,
        create_invoice,
        create_bill,
        create_deposit,
        create_payment,
        generate_pl_report,
        generate_balance_sheet,

        # Optimizaciones
        get_relevant_tools,
        build_conversation_context,
        necesita_chart,

        # Session state
        session_state,
        conversation_history,

        # Tools
        TOOL_FUNCTIONS
    )
    print(f"{Fore.GREEN}✅ Módulo main.py importado exitosamente{Style.RESET_ALL}")
except ImportError as e:
    print(f"{Fore.RED}❌ Error importando main.py: {e}{Style.RESET_ALL}")
    sys.exit(1)

def test_imports():
    """Test 1: Verificar importaciones de módulos de autonomía"""
    try:
        # Verificar que los módulos de autonomía se importaron
        from main import (
            # Nivel 1
            tool_search_web,
            tool_search_qbo_docs,
            # Nivel 2
            tool_create_journal_entry,
            tool_create_transfer,
            # Nivel 3
            tool_execute_python,
            # Bank Feed
            tool_analyze_bank_feed_for_classification,
            # User Learning
            tool_learn_from_interaction
        )
        return {'success': True, 'modules': 7}
    except ImportError as e:
        return {'success': False, 'error': str(e)}

def test_optimizations():
    """Test 2: Verificar funciones de optimización"""
    results = {}

    # Test get_relevant_tools
    tools = get_relevant_tools("clasifica transacciones de orrstown")
    results['get_relevant_tools'] = len(tools) > 0 and len(tools) < len(TOOL_FUNCTIONS)
    print(f"  → get_relevant_tools: {len(tools)}/{len(TOOL_FUNCTIONS)} tools")

    # Test build_conversation_context
    test_history = [
        {'role': 'user', 'content': 'mensaje 1'},
        {'role': 'assistant', 'content': 'respuesta 1'},
        {'role': 'user', 'content': 'mensaje 2'},
    ]
    recent, context = build_conversation_context(test_history, max_turns=2)
    results['build_conversation_context'] = len(recent) <= 4  # 2 turnos = 4 mensajes max
    print(f"  → build_conversation_context: {len(recent)} mensajes de {len(test_history)}")

    # Test necesita_chart
    results['necesita_chart_true'] = necesita_chart("clasifica transacciones")
    results['necesita_chart_false'] = not necesita_chart("cuánto gasté")
    print(f"  → necesita_chart('clasifica'): {results['necesita_chart_true']}")
    print(f"  → necesita_chart('cuánto gasté'): {not results['necesita_chart_false']}")

    return {'success': all(results.values()), 'details': results}

def test_chart_of_accounts():
    """Test 3: Cargar Chart of Accounts"""
    chart = load_chart_of_accounts()

    if not chart:
        return {'success': False, 'error': 'Chart vacío'}

    # chart es un diccionario {id: data}
    first_id = list(chart.keys())[0] if chart else None
    print(f"  → {len(chart)} cuentas cargadas")
    print(f"  → Ejemplo: {chart[first_id]['name'] if first_id else 'N/A'}")

    return {'success': True, 'count': len(chart)}

def test_search_functions():
    """Test 4: Funciones de búsqueda"""
    results = {}

    # Buscar customer (puede no existir, solo verificar que no crashee)
    try:
        customers = search_customer("Test")
        results['search_customer'] = True
        print(f"  → search_customer('Test'): {len(customers)} resultados")
    except Exception as e:
        results['search_customer'] = False
        print(f"  → search_customer ERROR: {e}")

    # Buscar vendor
    try:
        vendors = search_vendor("Test")
        results['search_vendor'] = True
        print(f"  → search_vendor('Test'): {len(vendors)} resultados")
    except Exception as e:
        results['search_vendor'] = False
        print(f"  → search_vendor ERROR: {e}")

    # Buscar cuenta
    try:
        accounts = find_account("Checking")
        results['find_account'] = True
        print(f"  → find_account('Checking'): {len(accounts)} resultados")
    except Exception as e:
        results['find_account'] = False
        print(f"  → find_account ERROR: {e}")

    return {'success': all(results.values()), 'details': results}

def test_tool_definitions():
    """Test 5: Verificar definiciones de tools"""
    required_tools = [
        'buscar_cliente',
        'buscar_vendor',
        'buscar_cuenta',
        'generar_reporte_pl',
        'generar_balance_sheet',
        'crear_invoice',
        'crear_bill',
        'crear_deposito',
        'refrescar_chart_accounts'
    ]

    missing = [tool for tool in required_tools if tool not in TOOL_FUNCTIONS]

    print(f"  → Tools totales: {len(TOOL_FUNCTIONS)}")
    print(f"  → Tools requeridas: {len(required_tools)}")
    print(f"  → Faltantes: {len(missing)}")

    if missing:
        print(f"  → Missing tools: {', '.join(missing)}")

    return {'success': len(missing) == 0, 'total': len(TOOL_FUNCTIONS), 'missing': missing}

def test_autonomy_tools():
    """Test 6: Verificar tools de autonomía"""
    autonomy_tools = [
        'buscarenweb',
        'buscardocsqbo',
        'crearasientodiario',
        'creartransferencia',
        'ejecutarcodigo',
        'analizarbankfeed',
        'aprenderinteraccion'
    ]

    present = [tool for tool in autonomy_tools if tool in TOOL_FUNCTIONS]
    missing = [tool for tool in autonomy_tools if tool not in TOOL_FUNCTIONS]

    print(f"  → Autonomía tools presentes: {len(present)}/{len(autonomy_tools)}")

    if missing:
        print(f"  → Faltantes: {', '.join(missing)}")

    return {'success': len(missing) == 0, 'present': present, 'missing': missing}

def test_session_state():
    """Test 7: Verificar session state"""
    required_keys = ['start_time', 'input_tokens', 'output_tokens', 
                     'operations', 'chart_of_accounts']

    missing = [key for key in required_keys if key not in session_state]

    print(f"  → Session keys: {len(session_state)}")
    print(f"  → Required keys: {len(required_keys)}")

    if missing:
        print(f"  → Missing: {', '.join(missing)}")

    return {'success': len(missing) == 0, 'details': dict(session_state)}

def test_tool_parameters():
    """Test 8: Verificar parámetros de tools (schemas)"""
    from main import TOOLS
    errors = []

    for tool in TOOLS:
        tool_name = tool["function"]["name"]
        if 'description' not in tool["function"]:
            errors.append(f"{tool_name}: missing description")

        if 'parameters' not in tool["function"]:
            errors.append(f"{tool_name}: missing parameters")
        elif 'properties' not in tool["function"]['parameters']:
            errors.append(f"{tool_name}: missing parameters.properties")

    print(f"  → Tools validadas: {len(TOOLS)}")
    print(f"  → Errores encontrados: {len(errors)}")

    if errors:
        for error in errors[:5]:  # Mostrar solo primeros 5
            print(f"    • {error}")

    return {'success': len(errors) == 0, 'errors': errors}

def test_environment_vars():
    """Test 9: Verificar variables de entorno"""
    required_vars = [
        'OPENROUTER_API_KEY',
        'QB_ACCESS_TOKEN',
        'QB_REFRESH_TOKEN',
        'QB_CLIENT_ID',
        'QB_CLIENT_SECRET',
        'QB_REALM_ID'
    ]

    missing = []
    present = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            present.append(var)
            # Mostrar primeros caracteres
            preview = value[:10] + '...' if len(value) > 10 else value
            print(f"  → {var}: {preview}")

    if missing:
        print(f"{Fore.YELLOW}  ⚠️  Variables faltantes: {', '.join(missing)}{Style.RESET_ALL}")

    return {
        'success': len(missing) == 0,
        'present': present,
        'missing': missing
    }

def test_file_structure():
    """Test 10: Verificar estructura de archivos"""
    required_files = [
        'main.py',
        '.env',
        'ocr_bills.py',
        'autonomia/__init__.py',
        'autonomia/autonomia_nivel1_websearch.py',
        'autonomia/autonomia_nivel2_api_explorer.py',
        'autonomia/autonomia_nivel3_code_executor.py',
        'autonomia/bank_feed_intelligence.py',
        'autonomia/user_behavior_learning.py',
        'autonomia/dynamic_report_generator.py'
    ]

    required_dirs = [
        'Backup',
        'autonomia',
        'Pending bills',
        'Processed bills'
    ]

    missing_files = [f for f in required_files if not os.path.exists(f)]
    missing_dirs = [d for d in required_dirs if not os.path.isdir(d)]

    print(f"  → Archivos requeridos: {len(required_files) - len(missing_files)}/{len(required_files)}")
    print(f"  → Directorios requeridos: {len(required_dirs) - len(missing_dirs)}/{len(required_dirs)}")

    if missing_files:
        print(f"{Fore.YELLOW}  ⚠️  Archivos faltantes: {', '.join(missing_files)}{Style.RESET_ALL}")

    if missing_dirs:
        print(f"{Fore.YELLOW}  ⚠️  Directorios faltantes: {', '.join(missing_dirs)}{Style.RESET_ALL}")

    return {
        'success': len(missing_files) == 0 and len(missing_dirs) == 0,
        'missing_files': missing_files,
        'missing_dirs': missing_dirs
    }

# MAIN TEST EXECUTION
if __name__ == '__main__':
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║           🧪 TEST SUITE - TMP AI ASSISTANT                          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    runner = TestRunner()

    # Ejecutar tests
    runner.test("Importaciones de módulos de autonomía", test_imports)
    runner.test("Funciones de optimización", test_optimizations)
    runner.test("Chart of Accounts", test_chart_of_accounts)
    runner.test("Funciones de búsqueda", test_search_functions)
    runner.test("Definiciones de tools", test_tool_definitions)
    runner.test("Tools de autonomía", test_autonomy_tools)
    runner.test("Session state", test_session_state)
    runner.test("Parámetros de tools", test_tool_parameters)
    runner.test("Variables de entorno", test_environment_vars)
    runner.test("Estructura de archivos", test_file_structure)

    # Resumen
    runner.summary()

    # Exit code
    sys.exit(0 if runner.failed == 0 else 1)
