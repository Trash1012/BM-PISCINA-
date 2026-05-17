from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import psycopg2
import time
from datetime import datetime

# ── PostgreSQL ─────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "whatsapp_metrics",  # ← cambia
    "user":     "postgres",          # ← cambia
    "password": "tu_password"        # ← cambia
}

def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sesiones (
            id          SERIAL PRIMARY KEY,
            contacto    VARCHAR(100),
            estado      VARCHAR(100),
            timestamp   TIMESTAMP DEFAULT NOW()
        )
    ''')
    conn.commit()
    return conn

def registrar(conn, contacto, estado):
    c = conn.cursor()
    c.execute(
        "INSERT INTO sesiones (contacto, estado) VALUES (%s, %s)",
        (contacto, estado)
    )
    conn.commit()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {contacto} → {estado}")

# ── WhatsApp Web ───────────────────────────────────────
def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=./perfil_chrome")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def get_estado(driver, nombre_contacto):
    try:
        estado_elem = driver.find_element(By.XPATH,
            f'//span[@title="{nombre_contacto}"]/../..//span[contains(@class,"_11JPr")]')
        return estado_elem.text
    except:
        return None

# ── Main ───────────────────────────────────────────────
CONTACTO = "Nombre exacto del contacto"  # ← cambia
INTERVALO = 30  # segundos

conn = init_db()
driver = iniciar_driver()

driver.get("https://web.whatsapp.com")
input("Escanea el QR y presiona ENTER para comenzar...")

try:
    chat = driver.find_element(By.XPATH, f'//span[@title="{CONTACTO}"]')
    chat.click()
    time.sleep(2)
except:
    print("Contacto no encontrado. Verifica el nombre exacto.")
    driver.quit()
    exit()

ultimo_estado = None

while True:
    estado = get_estado(driver, CONTACTO)
    if estado and estado != ultimo_estado:
        registrar(conn, contacto, estado)
        ultimo_estado = estado
    time.sleep(INTERVALO)