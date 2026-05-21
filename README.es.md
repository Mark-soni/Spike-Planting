# Spike Planting 💣

> 🌐 [English Version](README.md)

Overlay con contador regresivo global para Valorant. Mantén `4` por 2 segundos para iniciar una cuenta regresiva de 45 segundos — funciona aunque el juego esté en foco.

## Características

- Mantén `4` por 2 segundos para activar el contador
- Overlay siempre encima — funciona sobre Valorant, Chrome, cualquier app
- Recuerda la posición entre sesiones (arrástralo donde quieras)
- **No roba el foco ni minimiza el juego**
- Opcional: agrega tu propio video encima del contador

## Controles

| Tecla | Acción |
|-------|--------|
| Mantener `4` (2s) | Iniciar contador |
| `Ctrl+Q` | Ocultar overlay |
| `Ctrl+Shift+Q` | Cerrar app |

## Requisitos

- Python 3.x

```
pip install keyboard
```

> Opcional (solo si quieres un video encima del contador):
> ```
> pip install opencv-python Pillow
> ```

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

# Video opcional encima del contador (dejar vacío para desactivar)
VIDEO_PATH     = r''   # ej: r'C:\Videos\spike.webm'
```

## Licencia

MIT — libre para usar, modificar y compartir.

---

Built with the help of [Claude](https://claude.ai) (Anthropic)
