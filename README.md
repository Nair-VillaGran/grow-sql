# SQL Query Formatter

Una herramienta de consola para formatear y analizar consultas SQL con capacidades de IA.

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clona este repositorio o descarga los archivos
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Crea un archivo `.env` en la raíz del proyecto y agrega tu token de OpenRouter:
```
OPENROUTER_API_KEY=tu_token_aquí
```

## Uso

Ejecuta el programa:
```bash
python main.py
```

## Características

- Formateo de consultas SQL
- Análisis de consultas con IA (requiere configuración de OpenRouter)
- Interfaz de consola interactiva con colores
- Logo personalizable
- Recomendaciones de optimización
- Explicación de consultas SQL

## Nota

La funcionalidad de IA requiere una configuración válida de OpenRouter. Si no está configurada, esta opción estará deshabilitada pero el resto de funcionalidades seguirán disponibles. 