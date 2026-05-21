# Spike Planting 💣

Overlay para Valorant que muestra una animación de la Spike con un contador regresivo de 45 segundos al mantener la tecla `4`. Funciona en segundo plano aunque el juego esté en foco.

## Características

- Mantén `4` por 2 segundos para activar el contador
- Animación de la Spike sincronizada con los 45 segundos
- Overlay siempre encima — funciona sobre Valorant, Chrome, cualquier app
- Recuerda la posición entre sesiones (arrástralo donde quieras)
- **No roba el foco ni minimiza el juego**

## Controles

| Tecla | Acción |
|-------|--------|
| Mantener `4` (2s) | Iniciar contador |
| `Ctrl+Q` | Ocultar overlay |
| `Ctrl+Shift+Q` | Cerrar app |

## Requisitos

- Python 3.x
- Tu propio archivo de video `Spike.webm` (pon la ruta en `countdown.py`)

```
pip install keyboard opencv-python Pillow
```

## Uso

Ejecuta como **Administrador** (requerido para el hook global de teclado):

```
iniciar.bat
```

O manualmente:

```
python countdown.py
```

> **Nota:** Valorant debe estar en modo **Borderless Windowed** para que el overlay aparezca encima.

## Configuración

Edita las primeras líneas de `countdown.py` para personalizar:

```python
TOTAL_SECONDS  = 45    # duración del contador
HOLD_SECONDS   = 2     # segundos que hay que mantener '4' para activar
TRIGGER_KEY    = '4'   # tecla a mantener
SPIKE_OFFSET_X = 290   # posición horizontal de la Spike en el video
HALF_CROP      = 380   # nivel de zoom (mayor = más alejado)
```

## Licencia

MIT — libre para usar, modificar y compartir.
