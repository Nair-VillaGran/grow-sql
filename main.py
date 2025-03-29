#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Grow SQL: Herramienta profesional para formatear y analizar consultas SQL.
"""

import os
import sys
import time
import json
from typing import Dict, Any, Optional, Tuple, List

# Third-party imports
import sqlparse
import requests
from dotenv import load_dotenv
from pyfiglet import Figlet
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.status import Status

# --- Constantes ---
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_AI_MODEL = "deepseek/deepseek-chat-v3-0324:free"
REQUEST_TIMEOUT = 60  # Segundos

# Mensajes de Sistema para IA
SYSTEM_PROMPT_RECOMMENDATIONS = (
    "Eres un experto analista de SQL. Debes evaluar consultas SQL y proporcionar "
    "recomendaciones detalladas en español sobre optimización, buenas prácticas y "
    "posibles mejoras. Sé específico y profesional en tus respuestas. "
    "Formatea la respuesta para que sea compatible en una terminal, ya que el resultado o el mensaje respuesta se muestra en la terminal"
)
SYSTEM_PROMPT_EXPLANATION = (
    "Eres un experto explicando consultas SQL a desarrolladores. Explica en detalle "
    "cómo funciona la consulta SQL proporcionada, paso a paso, de forma clara y "
    "concisa en español. Formatea la respuesta para que sea compatible en una terminal, ya que el resultado o el mensaje respuesta se muestra en la terminal"
)

# Mensajes de Usuario
MSG_ASK_SQL_QUERY = "\n[bold yellow]Ingresa tu consulta SQL:[/bold yellow]"
MSG_ASK_CONTINUE = "\n¿Deseas realizar otra operación?"
MSG_THANKS = "\n[bold blue]¡Gracias por usar Grow SQL![/bold blue]"
MSG_API_KEY_ERROR = (
    "[bold red]Error:[/bold red] La funcionalidad de IA no está disponible. "
    "Configura tu token de OpenRouter (OPENROUTER_API_KEY) en el archivo .env"
)
MSG_API_WAIT_NOTE = (
    "[yellow]Nota:[/yellow] La API puede tardar hasta "
    f"{REQUEST_TIMEOUT} segundos o más en responder..."
)

# --- Configuración ---
load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
AI_MODEL = os.getenv('AI_MODEL', DEFAULT_AI_MODEL)
SITE_URL = os.getenv('SITE_URL', "https://github.com/Nair-Villagran/grow-sql") # Ejemplo
SITE_NAME = os.getenv('SITE_NAME', "Grow SQL") # Ejemplo

# --- Inicialización ---
console = Console()

# --- Funciones Auxiliares ---

def print_header() -> None:
    """Imprime la cabecera de la aplicación con ASCII art."""
    try:
        custom_fig = Figlet(font='big', width=console.width)
        ascii_art = custom_fig.renderText(SITE_NAME)
    except Exception: # Fallback si pyfiglet falla
        ascii_art = SITE_NAME

    console.print(Panel.fit(
        f"[bold cyan]{ascii_art}[/]\n"
        f"[italic yellow]Herramienta profesional para formatear y analizar consultas SQL[/]",
        border_style="bright_blue",
        padding=(1, 2),
        title="[bold magenta]v1.1[/]", # Versión actualizada
        subtitle=f"[green]by @Nair-Villagran ({SITE_URL})[/green]"
    ))

def format_sql(query: str) -> str:
    """Formatea la consulta SQL usando sqlparse."""
    try:
        formatted = sqlparse.format(query, reindent=True, keyword_case='upper')
        return formatted
    except Exception as e:
        console.print(f"[bold red]Error al formatear SQL:[/bold red] {e}")
        return query # Devuelve la consulta original en caso de error

def _call_openrouter_api(messages: List[Dict[str, str]], status: Status) -> Tuple[Optional[Dict[str, Any]], Optional[str], float]:
    """
    Realiza la llamada a la API de OpenRouter.

    Retorna:
        Tuple[Optional[Dict[str, Any]], Optional[str], float]:
            (datos_respuesta, mensaje_error, duracion)
    """
    start_time = time.time()
    if not OPENROUTER_API_KEY:
        return None, MSG_API_KEY_ERROR, 0.0

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": SITE_URL, # Opcional, recomendado por OpenRouter
        "X-Title": SITE_NAME,     # Opcional, recomendado por OpenRouter
    }
    data = {
        "model": AI_MODEL,
        "messages": messages,
        # "temperature": 0.7, # Puedes añadir más parámetros si lo deseas
    }

    try:
        status.update(f"[bold green]Enviando solicitud a {AI_MODEL}...[/bold green]")
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=data,
            timeout=REQUEST_TIMEOUT
        )
        duration = time.time() - start_time
        response.raise_for_status() # Lanza HTTPError para respuestas 4xx/5xx
        return response.json(), None, duration

    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        return None, f"La solicitud excedió el tiempo máximo de espera ({REQUEST_TIMEOUT}s).", duration
    except requests.exceptions.RequestException as e:
        duration = time.time() - start_time
        error_detail = f"Error de red/API: {e}"
        if e.response is not None:
            try:
                error_detail += f" - {e.response.text}"
            except Exception:
                pass # Ignorar si no se puede leer el cuerpo de la respuesta
        return None, error_detail, duration
    except json.JSONDecodeError:
        duration = time.time() - start_time
        return None, "Error al decodificar la respuesta JSON de la API.", duration
    except Exception as e:
        duration = time.time() - start_time
        return None, f"Error inesperado durante la llamada API: {e}", duration

def get_ai_analysis(query: str, analysis_type: str = "recommendations") -> Dict[str, Any]:
    """
    Obtiene análisis de IA (recomendaciones o explicación) para la consulta SQL.

    Args:
        query (str): La consulta SQL a analizar.
        analysis_type (str): 'recommendations' o 'explanation'.

    Returns:
        Dict[str, Any]: {
            'success': bool,
            'content': Optional[str],
            'error': Optional[str],
            'duration': float
        }
    """
    if analysis_type == "recommendations":
        system_prompt = SYSTEM_PROMPT_RECOMMENDATIONS
        user_prompt = f"Por favor analiza la siguiente consulta SQL y proporciona recomendaciones concisas para mejorarla:\n\n```sql\n{query}\n```"
    elif analysis_type == "explanation":
        system_prompt = SYSTEM_PROMPT_EXPLANATION
        user_prompt = f"Explica en detalle cómo funciona esta consulta SQL:\n\n```sql\n{query}\n```"
    else:
        return {"success": False, "content": None, "error": "Tipo de análisis no válido", "duration": 0.0}

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    console.print(f"\n[yellow][{time.strftime('%H:%M:%S')}] Iniciando solicitud a la IA ({analysis_type})...[/yellow]")
    console.print(MSG_API_WAIT_NOTE)

    result_data: Optional[Dict[str, Any]] = None
    error_msg: Optional[str] = None
    duration: float = 0.0

    try:
        with console.status("[bold green]Procesando solicitud a la IA...[/bold green]", spinner="dots") as status:
            result_data, error_msg, duration = _call_openrouter_api(messages, status)
    except KeyboardInterrupt:
        console.print("\n[bold red]Operación cancelada por el usuario.[/bold red]")
        return {"success": False, "content": None, "error": "Cancelado por usuario", "duration": time.time() - start_time if 'start_time' in locals() else 0.0} # Asegura que start_time exista

    console.print(f"[yellow][{time.strftime('%H:%M:%S')}] Solicitud completada en {duration:.2f}s[/yellow]")

    if error_msg:
        return {"success": False, "content": None, "error": error_msg, "duration": duration}

    if result_data and 'choices' in result_data and len(result_data['choices']) > 0:
        # Asegurarse de que la estructura esperada exista
        try:
            content = result_data['choices'][0]['message']['content']
            # Aquí podrías añadir validación del contenido si es necesario
            return {"success": True, "content": content.strip(), "error": None, "duration": duration}
        except (KeyError, IndexError, TypeError) as e:
            error_detail = f"Estructura de respuesta inesperada de la API: {e} - Datos: {result_data}"
            return {"success": False, "content": None, "error": error_detail, "duration": duration}
    else:
        error_detail = f"Respuesta vacía o inválida de la API: {result_data}"
        return {"success": False, "content": None, "error": error_detail, "duration": duration}

def _check_api_key() -> bool:
    """Verifica si la API key está presente y muestra un error si no."""
    if not OPENROUTER_API_KEY:
        console.print(MSG_API_KEY_ERROR)
        return False
    return True

def _ask_to_continue() -> bool:
    """Pregunta al usuario si desea realizar otra operación."""
    try:
        choice = Prompt.ask(MSG_ASK_CONTINUE, choices=["s", "n"], default="s")
        return choice.lower() == "s"
    except KeyboardInterrupt:
        return False # Si cancela, asumimos que no quiere continuar

# --- Manejadores de Opciones del Menú ---

def _handle_format_only() -> None:
    """Maneja la opción de solo formatear."""
    try:
        query = Prompt.ask(MSG_ASK_SQL_QUERY)
        if not query.strip():
            console.print("[yellow]Advertencia:[/yellow] Consulta vacía.")
            return
        formatted_query = format_sql(query)
        console.print("\n[bold green]Consulta formateada:[/bold green]")
        # Usar Panel para mejor visualización de bloques de código
        console.print(Panel(formatted_query, border_style="dim", expand=False))
    except KeyboardInterrupt:
        console.print("\n[bold red]Operación cancelada.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error inesperado:[/bold red] {e}")


def _handle_format_and_recommend() -> None:
    """Maneja la opción de formatear y obtener recomendaciones."""
    if not _check_api_key():
        return
    try:
        query = Prompt.ask(MSG_ASK_SQL_QUERY)
        if not query.strip():
            console.print("[yellow]Advertencia:[/yellow] Consulta vacía.")
            return

        formatted_query = format_sql(query)
        console.print("\n[bold green]Consulta formateada:[/bold green]")
        console.print(Panel(formatted_query, border_style="dim", expand=False))

        console.print("\n[bold blue]Obteniendo recomendaciones de IA...[/bold blue]")
        result = get_ai_analysis(query, "recommendations")

        if result["success"] and result["content"]:
            console.print("\n[bold magenta]Recomendaciones de IA:[/bold magenta]")
            console.print(Panel(result["content"], border_style="magenta", title="Análisis IA", expand=False))
            minutes = int(result['duration'] // 60)
            seconds = result['duration'] % 60
            console.print(f"\n[dim]Tiempo de análisis IA: {minutes}m {seconds:.2f}s[/dim]")
        else:
            console.print(f"[bold red]Error al obtener recomendaciones:[/bold red] {result['error']}")

    except KeyboardInterrupt:
        console.print("\n[bold red]Operación cancelada.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error inesperado:[/bold red] {e}")


def _handle_explain() -> None:
    """Maneja la opción de explicar la consulta."""
    if not _check_api_key():
        return
    try:
        query = Prompt.ask(MSG_ASK_SQL_QUERY)
        if not query.strip():
            console.print("[yellow]Advertencia:[/yellow] Consulta vacía.")
            return

        console.print("\n[bold blue]Obteniendo explicación de la IA...[/bold blue]")
        result = get_ai_analysis(query, "explanation")

        if result["success"] and result["content"]:
            console.print("\n[bold cyan]Explicación de la Consulta:[/bold cyan]")
            console.print(Panel(result["content"], border_style="cyan", title="Explicación IA", expand=False))
            minutes = int(result['duration'] // 60)
            seconds = result['duration'] % 60
            console.print(f"\n[dim]Tiempo de análisis IA: {minutes}m {seconds:.2f}s[/dim]")
        else:
            console.print(f"[bold red]Error al obtener explicación:[/bold red] {result['error']}")

    except KeyboardInterrupt:
        console.print("\n[bold red]Operación cancelada.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error inesperado:[/bold red] {e}")

# --- Menú Principal ---

def main_menu() -> None:
    """Muestra el menú principal y maneja la entrada del usuario."""
    actions = {
        "1": _handle_format_only,
        "2": _handle_format_and_recommend,
        "3": _handle_explain,
    }

    while True:
        console.print("\n" + "="*30)
        console.print("[bold blue]  Menú Principal[/bold blue]")
        console.print("="*30)
        console.print("1. Formatear consulta SQL")
        console.print("2. Formatear y obtener recomendaciones de IA")
        console.print("3. Explicar consulta SQL con IA")
        console.print("4. Salir")
        console.print("="*30)

        try:
            choice = Prompt.ask("\nSelecciona una opción", choices=["1", "2", "3", "4"], default="4")

            if choice == "4":
                break # Salir del bucle while

            action = actions.get(choice)
            if action:
                action() # Ejecutar la función correspondiente
            else:
                console.print("[red]Opción inválida.[/red]") # No debería ocurrir con choices

            # Preguntar si continuar solo si no eligió salir
            if not _ask_to_continue():
                break

        except KeyboardInterrupt:
            break # Salir si presiona Ctrl+C en el prompt del menú
        except Exception as e:
            console.print(f"[bold red]Error en el menú principal:[/bold red] {e}")
            # Opcional: decidir si continuar o salir en caso de error inesperado
            if not Prompt.ask("Ocurrió un error. ¿Intentar de nuevo?", choices=["s", "n"], default="s"):
                 break


    console.print(MSG_THANKS)

# --- Punto de Entrada ---

def main() -> None:
    """Función principal de la aplicación."""
    try:
        console.clear()
        print_header()
        main_menu()
    except KeyboardInterrupt:
        # Asegurarse de que el mensaje de gracias se imprima incluso si se interrumpe globalmente
        console.print(MSG_THANKS)
    except Exception as e:
        console.print(f"\n[bold red]Error fatal en la aplicación:[/bold red] {e}")
        # Podrías añadir logging aquí
        sys.exit(1) # Salir con código de error

if __name__ == "__main__":
    main()
