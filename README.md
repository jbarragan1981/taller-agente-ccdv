# Taller práctico · Agente de soporte con la API de Claude

Preparación para **Claude Certified Developer – Foundations (CCDV-F)** · Viamatica

> *Writing code that uses Claude is different from using Claude to write code.*

En este taller construyes, paso a paso, el backend de un agente de soporte para TiendaTech. El frontend ya está listo: cada paso que completas en Python enciende una capacidad nueva en la pantalla.

| Paso | Archivo | Qué programas | Qué aparece en el front | Tiempo |
|---|---|---|---|---|
| 1 | `app/paso1_chat.py` | Messages API con system prompt e historial | El chat responde y recuerda la conversación | 7 min |
| 2 | `app/paso2_clasificador.py` | Diagnóstico de prompt: constraint, XML y few-shot | Etiqueta BILLING / TECHNICAL / ESCALATION bajo cada mensaje | 12 min |
| 3 | `app/paso3_extraccion.py` | Structured outputs con JSON schema y `stop_reason` | Tarjeta "Ticket" con cliente, categoría y prioridad | 10 min |
| 4 | `app/paso4_agente.py` | Tool use: el loop del agente y la regla de carry-back | Panel "Herramientas" con cada llamada | 10 min |
| 5 | `app/paso5_thinking.py` | Extended thinking adaptativo y `effort` | Interruptor "Pensar" y panel "Razonamiento" | 6 min |

El panel **Debug** muestra en todo momento `stop_reason`, tokens y los content blocks de cada llamada a la API.

---

## 1. Arranque

### Opción A · GitHub Codespaces (recomendada)

1. En este repositorio: **Code › Codespaces › Create codespace on main**.
2. Cuando lo pida, pega la API key que te dio la instructora en el secret `ANTHROPIC_API_KEY`. Si no te lo pide, crea el archivo `.env` (paso 3 de la opción B).
3. Espera a que termine la instalación y ejecuta en la terminal:

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. Codespaces abre la vista previa del puerto 8000. Si no, ve a la pestaña **Ports** y abre el 8000 en el navegador.

### Opción B · En tu computadora con VS Code

Necesitas Python 3.10 o superior y git.

```bash
git clone https://github.com/jbarragan1981/taller-agente-ccdv.git
cd taller-agente-ccdv
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

Abre `.env` y pega la clave en `ANTHROPIC_API_KEY=`. Luego levanta el servidor con `uvicorn app.main:app --reload --port 8000` o con **F5** (configuración "Taller: levantar el agente") y abre <http://localhost:8000>.

Con `--reload`, cada vez que guardas un archivo el servidor se reinicia solo: guarda y vuelve a escribir en el chat.

> ⚠️ Nunca escribas la clave dentro del código ni la subas al repositorio. El archivo `.env` está en `.gitignore`.

---

## 2. Cómo está armado

```
Navegador (static/index.html)
   │  POST /api/chat  con TODO el historial
   ▼
app/main.py ──┬── paso2_clasificador.clasificar()      → etiqueta
              ├── paso3_extraccion.extraer_ticket()    → ticket JSON
              └── paso4_agente.agente()                → respuesta + herramientas
                     (o paso1_chat.responder() si el Paso 4 no está listo)
                  paso5_thinking.opciones_razonamiento() → thinking / effort para 1 y 4
```

- `app/cliente.py` crea el cliente de Anthropic y tiene utilidades para el panel Debug. **No lo tocas.**
- `app/herramientas.py` tiene los datos simulados (pedidos A100, B200, C300 y cuatro políticas) y los tool schemas. **No lo tocas**, salvo en el reto final.
- `app/main.py` conecta todo y maneja errores de la API. **No lo tocas.**

Cada archivo de paso tiene huecos `...` con instrucciones `# TODO`. Mientras quede un `...`, el front muestra ese paso como pendiente en lugar de romperse.

---

## 3. Los pasos

### Paso 1 · Chat con la Messages API
Completa `texto_de()` y `responder()`. La respuesta llega como una lista de content blocks, así que filtras por tipo. Fíjate en el panel Debug: el contador "Mensajes enviados" crece con cada turno porque la API no guarda estado.

### Paso 2 · Laboratorio de diagnóstico
Este paso ya corre, pero el clasificador devuelve oraciones en vez de etiquetas y el front las marca en rojo. Usa la tabla de la teoría para diagnosticar y corrige `SYSTEM_CLASIFICADOR` con estructura:

| Lo que observas | Lo que falta |
|---|---|
| Forma incorrecta (oración en vez de etiqueta) | Output constraint |
| El contenido se desvía de alcance o tono | System prompt más específico |
| Entiende la tarea pero inventa la estructura | Few-shot examples |
| Funciona en casos simples y falla en un caso borde | Constraint o ejemplo para ese caso |

Prueba los ejemplos del front, en especial el ambiguo ("Me cobraron dos veces y además la app dejó de abrir") y el que intenta cambiar las instrucciones. Si tres cambios seguidos no mejoran nada, para y vuelve a diagnosticar.

### Paso 3 · Structured outputs
Llama a la API con `output_config` y el `SCHEMA_TICKET`, y revisa `stop_reason` antes de parsear. Para comprobar tu manejo de errores, baja `MAX_TOKENS_EXTRACCION` a 20: la tarjeta debe mostrar el error sin que el servidor falle.

### Paso 4 · El loop del agente
Completa los cinco TODO del loop. Después prueba "Compara mis pedidos A100 y C300": en Debug verás una vuelta con dos bloques `tool_use` (llamadas en paralelo). Prueba también un pedido que no existe, como X999, para ver `is_error`.

### Paso 5 · Thinking y effort
Completa `opciones_razonamiento()`, activa "Pensar" y compara `output_tokens` entre `low`, `medium` y `high`. Con thinking activo y herramientas, el TODO 2 del Paso 4 (carry-back) es lo que evita que la API rechace la segunda vuelta.

---

## 4. ¿Te quedaste atrás? Usa los checkpoints

Cada rama tiene resueltos los pasos hasta ese número:

| Rama | Contiene |
|---|---|
| `main` | Punto de partida |
| `paso-1` … `paso-5` | Pasos resueltos hasta ese número |
| `solucion` | Todo resuelto |

```bash
git stash                 # guarda tus cambios (opcional)
git checkout paso-3       # salta al estado con los pasos 1 a 3 resueltos
```

Para ver solo la solución de un paso en GitHub, compara ramas, por ejemplo `paso-2...paso-3`.

---

## 5. Retos si te sobra tiempo

1. **Human in the loop:** agrega en `herramientas.py` una herramienta `cancelar_pedido` y, antes de ejecutarla en el loop, exige una confirmación (por ejemplo, que el usuario escriba "CONFIRMO"). Las acciones irreversibles necesitan un humano en el loop.
2. **Streaming:** crea un endpoint que use `client.messages.stream()` y envíe el texto al front con Server-Sent Events.
3. **Selección de herramienta:** crea dos herramientas con descripciones parecidas y observa cómo Claude se confunde. Luego arregla las descripciones.

---

## 6. Problemas comunes

| Síntoma | Qué hacer |
|---|---|
| Banner rojo "Falta la API key" | Crea `.env` con la clave o configura el secret, y reinicia `uvicorn` |
| "La API key no es válida" | Revisa que la pegaste completa, sin espacios |
| "Límite de peticiones alcanzado" | La clave es compartida: espera unos segundos y reenvía |
| Error 400 mencionando el modelo | Cambia `CLAUDE_MODEL` en `.env` por uno disponible para la clave |
| El front no cambia después de editar | Guarda el archivo y revisa errores de sintaxis en la terminal de `uvicorn` |

## Créditos

Ejercicios inspirados en el repositorio [Claude-Certified-Developer-CCDV-F](https://github.com/kuljotSB/Claude-Certified-Developer-CCDV-F) y en el Módulo 2 del curso de Developer de Anthropic. Los datos de TiendaTech son ficticios.
