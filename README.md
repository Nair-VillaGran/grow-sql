# Grow SQL: Formateador y Analizador Inteligente de Consultas SQL

**Grow SQL** es una herramienta de línea de comandos (CLI) diseñada para formatear, analizar y optimizar tus consultas SQL, potenciada con capacidades de Inteligencia Artificial.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Características Principales

*   **Formateo Automático:** Aplica un estilo consistente y legible a tus consultas SQL.
*   **Análisis con IA:** Obtén explicaciones detalladas y recomendaciones de optimización para tus consultas (requiere configuración de API).
*   **Interfaz Interactiva:** Disfruta de una experiencia de usuario amigable en la consola con resaltado de sintaxis.
*   **Logo Personalizable:** Añade un toque visual a la herramienta.

## Requisitos Previos

*   Python 3.8 o superior.
*   `pip` (Gestor de paquetes de Python).
*   Git (para clonar el repositorio).

## Instalación y Configuración

Sigue estos pasos para poner en marcha Grow SQL:

1.  **Clona el Repositorio:**
    ```bash
    git clone https://github.com/Nair-VillaGran/grow-sql.git
    cd grow-sql
    ```

2.  **Crea y Activa un Entorno Virtual (Recomendado):**
    Es una buena práctica aislar las dependencias del proyecto.
    ```bash
    # Crea el entorno virtual (si no existe)
    python -m venv venv

    # Activa el entorno virtual
    # En Linux/macOS:
    source venv/bin/activate
    # En Windows (Git Bash o WSL):
    # source venv/Scripts/activate
    # En Windows (Command Prompt):
    # venv\Scripts\activate.bat
    # En Windows (PowerShell):
    # venv\Scripts\Activate.ps1
    ```
    *Verás `(venv)` al principio de la línea de comandos si la activación fue exitosa.*

3.  **Instala las Dependencias:**
    Con el entorno virtual activado, instala las librerías necesarias.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura la API Key (Opcional):**
    Para usar las funciones de análisis con IA, necesitas una API key de OpenRouter.
    *   Crea un archivo llamado `.env` en la raíz del proyecto (puedes copiar `.env.example`).
    *   Añade tu API key al archivo `.env`:
        ```dotenv
        OPENROUTER_API_KEY=tu_api_key_aqui
        ```
    *   **Importante:** Asegúrate de que `.env` esté incluido en tu archivo `.gitignore` para no subir tu clave secreta al repositorio.

## Uso

Una vez instalado y configurado, ejecuta la herramienta desde la raíz del proyecto (asegúrate de que tu entorno virtual esté activado):

```bash
python main.py
```

Sigue las instrucciones interactivas en la consola para formatear o analizar tus consultas SQL.

## Nota sobre la IA

La funcionalidad de análisis y explicación mediante IA depende de una configuración válida de la API de OpenRouter en el archivo `.env`. Si no se proporciona una clave válida, estas opciones estarán deshabilitadas, pero las demás características (como el formateo) seguirán funcionando correctamente.

## Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar Grow SQL, por favor abre un *issue* o envía un *pull request*.
