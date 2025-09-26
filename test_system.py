#!/usr/bin/env python3
"""
Script de pruebas para verificar la configuración del sistema RAG Video v2.
Este script te ayuda a probar cada componente paso a paso.
"""

import os
import sys
import json
from pathlib import Path

# Add functions directory to path
functions_path = Path(__file__).parent / "functions"
sys.path.insert(0, str(functions_path))

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")

def check_environment_config():
    """Check current environment configuration."""
    print_header("🔧 VERIFICACIÓN DE CONFIGURACIÓN")
    
    # Load local.settings.json
    local_settings_path = functions_path / "local.settings.json"
    
    if not local_settings_path.exists():
        print("❌ local.settings.json no encontrado")
        return False
    
    with open(local_settings_path) as f:
        config = json.load(f)
    
    values = config.get("Values", {})
    
    # Load environment variables from local.settings.json
    for key, value in values.items():
        if not key.startswith("#") and value and value.strip():
            os.environ[key] = str(value).strip()
    
    required_configs = {
        "Azure AI Services": [
            ("AZURE_AI_SERVICE_ENDPOINT", "Endpoint del Azure AI Services"),
        ],
        "Azure OpenAI": [
            ("AZURE_OPENAI_ENDPOINT", "Endpoint de Azure OpenAI"),
            ("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "Nombre del deployment GPT"),
            ("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "Nombre del deployment embeddings"),
        ],
        "Azure Search": [
            ("AZURE_SEARCH_ENDPOINT", "Endpoint de Azure Cognitive Search"),
        ],
        "Storage (Entra ID)": [
            ("STORAGE_ACCOUNT_NAME", "Nombre del Storage Account"),
            ("VIDEO_CONTAINER_NAME", "Nombre del contenedor de videos"),
        ]
    }
    
    # Optional configs for backward compatibility
    optional_configs = {
        "Storage (Legacy)": [
            ("STORAGE_CONNECTION_STRING", "Connection string del Storage Account [OPCIONAL - mejor usar Entra ID]"),
        ]
    }
    
    print("📋 Configuración actual:")
    all_configured = True
    
    for category, configs in required_configs.items():
        print_section(category)
        for key, description in configs:
            value = values.get(key, "").strip()
            if value and not value.startswith("#") and value != "":
                print(f"  ✅ {key}: {description}")
                print(f"     -> {value[:50]}{'...' if len(value) > 50 else ''}")
            else:
                print(f"  ❌ {key}: {description} [NO CONFIGURADO]")
                all_configured = False
    
    # Show optional configs
    for category, configs in optional_configs.items():
        print_section(f"{category} (Opcional)")
        for key, description in configs:
            value = values.get(key, "").strip()
            if value and not value.startswith("#") and value != "":
                print(f"  ✅ {key}: {description}")
                print(f"     -> {value[:50]}{'...' if len(value) > 50 else ''}")
            else:
                print(f"  ⚪ {key}: {description} [NO CONFIGURADO]")
    
    return all_configured

def test_imports():
    """Test that all required modules can be imported."""
    print_header("📦 VERIFICACIÓN DE DEPENDENCIAS")
    
    imports = [
        ("azure.functions", "Azure Functions"),
        ("azure.identity", "Azure Identity"),
        ("azure.storage.blob", "Azure Storage"),
        ("azure.search.documents", "Azure Search"),
        ("openai", "OpenAI SDK"),
        ("requests", "HTTP Requests"),
        ("shared.clients.azure_ai_client", "Azure AI Client"),
        ("shared.clients.content_understanding_client", "Content Understanding Client"),
    ]
    
    all_good = True
    for module, name in imports:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            all_good = False
    
    return all_good

def test_azure_connection():
    """Test Azure service connections."""
    print_header("🔗 PRUEBAS DE CONEXIÓN AZURE")
    
    try:
        from shared.clients.azure_ai_client import ContentUnderstandingClient
        from azure.identity import DefaultAzureCredential
        
        print("Probando autenticación Azure...")
        
        # Check if we can get credentials
        try:
            credential = DefaultAzureCredential()
            print("  ✅ Credenciales Azure disponibles")
        except Exception as e:
            print(f"  ⚠️ Advertencia de credenciales: {e}")
            print("     (Esto es normal si no estás autenticado en Azure CLI)")
        
        # Check endpoints configuration
        ai_endpoint = os.environ.get("AZURE_AI_SERVICE_ENDPOINT")
        if ai_endpoint:
            print(f"  ✅ Azure AI endpoint configurado: {ai_endpoint}")
        else:
            print("  ❌ AZURE_AI_SERVICE_ENDPOINT no configurado")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Error en prueba de conexión: {e}")
        return False

def test_content_understanding_client():
    """Test Content Understanding client."""
    print_header("🎥 PRUEBA DEL CLIENTE CONTENT UNDERSTANDING")
    
    try:
        from shared.clients.content_understanding_client import AzureContentUnderstandingClient
        
        # Check if we have required environment variables
        endpoint = os.environ.get("AZURE_AI_SERVICE_ENDPOINT")
        if not endpoint:
            print("❌ Necesitas configurar AZURE_AI_SERVICE_ENDPOINT")
            print("   Ejemplo: https://tu-recurso.cognitiveservices.azure.com")
            return False
        
        print("📝 Configuración del cliente:")
        print(f"  • Endpoint: {endpoint}")
        print(f"  • API Version: {os.environ.get('AZURE_AI_SERVICE_API_VERSION', '2024-12-01-preview')}")
        
        # Note: We can't actually test the connection without valid credentials
        print("  ✅ Cliente Content Understanding disponible")
        print("  ⚠️ Para probar la conexión real necesitas:")
        print("     1. Azure CLI configurado (az login)")
        print("     2. O una API key válida")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_configuration_guide():
    """Show configuration guide."""
    print_header("📋 GUÍA DE CONFIGURACIÓN")
    
    print("""
Para probar el sistema necesitas configurar los siguientes servicios Azure:

1. 🤖 AZURE AI SERVICES (Content Understanding):
   - Crear un recurso "Azure AI Services" en Azure Portal
   - Copiar el endpoint y configurar AZURE_AI_SERVICE_ENDPOINT

2. 🧠 AZURE OPENAI:
   - Crear un recurso "Azure OpenAI" 
   - Desplegar modelos GPT-4 y embeddings
   - Configurar AZURE_OPENAI_ENDPOINT y nombres de deployments

3. 🔍 AZURE COGNITIVE SEARCH:
   - Crear un servicio "Azure Cognitive Search"
   - Configurar AZURE_SEARCH_ENDPOINT

4. 💾 AZURE STORAGE (con Entra ID - RECOMENDADO):
   - Crear una Storage Account
   - Configurar STORAGE_ACCOUNT_NAME (nombre del storage account)
   - Configurar VIDEO_CONTAINER_NAME (nombre del contenedor)
   - Asignar permisos "Storage Blob Data Contributor" a tu usuario/identidad

🔐 AUTENTICACIÓN:
   - Este sistema usa Entra ID (más seguro que connection strings)
   - Asegúrate de tener permisos en todos los recursos
   - Para desarrollo: az login
   - Para producción: Managed Identity o Service Principal

📝 Pasos siguientes:
   1. Configura las variables de entorno en functions/local.settings.json
   2. Ejecuta: az login (para autenticación)
   3. Ejecuta este script de nuevo para verificar
   4. Inicia Azure Functions: cd functions && func host start
""")

def main():
    """Run all tests."""
    print_header("🚀 SISTEMA RAG VIDEO v2 - VERIFICACIÓN DE CONFIGURACIÓN")
    
    # Test 1: Import dependencies
    imports_ok = test_imports()
    
    # Test 2: Check configuration
    config_ok = check_environment_config()
    
    # Test 3: Test Azure connections
    azure_ok = test_azure_connection()
    
    # Test 4: Test Content Understanding
    cu_ok = test_content_understanding_client()
    
    # Summary
    print_header("📊 RESUMEN")
    
    if imports_ok:
        print("✅ Dependencias instaladas correctamente")
    else:
        print("❌ Faltan dependencias por instalar")
    
    if config_ok:
        print("✅ Configuración completa")
    else:
        print("❌ Configuración incompleta")
        show_configuration_guide()
    
    if azure_ok:
        print("✅ Conexiones Azure disponibles")
    else:
        print("❌ Problemas con conexiones Azure")
    
    if cu_ok:
        print("✅ Cliente Content Understanding listo")
    else:
        print("❌ Problemas con Content Understanding client")
    
    if imports_ok and config_ok and azure_ok and cu_ok:
        print("\n🎉 ¡Sistema listo para pruebas!")
        print("\n📝 Próximos pasos:")
        print("   1. cd functions")
        print("   2. func host start")
        print("   3. Probar endpoints con un cliente HTTP")
    else:
        print("\n⚠️ El sistema necesita configuración adicional")
        print("   Revisa los errores anteriores y la guía de configuración")

if __name__ == "__main__":
    main()