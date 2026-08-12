import sys
import json
import urllib.request
import urllib.error

# Configuración por defecto
DEFAULT_URL = "http://localhost:8081/api/v1/integrations/checkmk/webhook"

def send_webhook(host_name, host_state, url=DEFAULT_URL):
    print(f"Simulando alerta Checkmk...")
    print(f"URL: {url}")
    print(f"Dispositivo: {host_name}")
    print(f"Estado: {host_state}")
    
    payload = {
        "host_name": host_name,
        "host_state": host_state,
        "service_state": "CRIT" if host_state == "CRITICAL" else None
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    # Ignore SSL verification for self-signed certificates or raw IP testing
    import ssl
    context = ssl._create_unverified_context()
    
    try:
        with urllib.request.urlopen(req, context=context) as response:
            res_body = response.read().decode("utf-8")
            print("\n🟢 Webhook procesado exitosamente!")
            print(json.dumps(json.loads(res_body), indent=2, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print(f"\n🔴 Error del Servidor ({e.code}): {e.reason}")
        print(e.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"\n🔴 Error de Conexión: {e.reason}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python mock_checkmk_webhook.py <nombre_host> <estado_host> [url_custom]")
        print("Ejemplo: python mock_checkmk_webhook.py switch_central_1 DOWN")
        print("\nEjecutando con valores de prueba por defecto...")
        # Fallback to test with a standard switch name from database seed
        # (e.g. SW-CO-01 is a common name in cmdb seed)
        send_webhook("SW-CO-01", "DOWN")
    else:
        host_name = sys.argv[1]
        host_state = sys.argv[2]
        url = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_URL
        send_webhook(host_name, host_state, url)
