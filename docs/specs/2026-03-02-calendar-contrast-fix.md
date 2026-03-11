# Spec: Correccion de contraste del calendario DatePickerInput

**Fecha:** 2026-03-02
**Tipo:** Bug fix (CSS)
**Archivo afectado:** `assets/dark_theme.css`

## Problema

El componente `dmc.DatePickerInput` (usado en `/ventas` y `/tablero`) tiene problemas de contraste con el dark theme:

1. **Titulos de meses y anios no legibles**: Al hacer click en el header del calendario para navegar a la vista de meses o anios, los textos no se distinguen del fondo.
2. **Rango seleccionado no legible con filtro cerrado**: Cuando el picker esta cerrado, el valor mostrado en el input (ej: "01/03/2026 - 02/03/2026") no tiene suficiente contraste.

## Analisis

### Componentes afectados

| Componente | Selector CSS | Estado actual | Problema |
|---|---|---|---|
| Input cerrado (valor mostrado) | `.mantine-DatePickerInput-input` | No tiene regla especifica | Texto hereda color oscuro, no se lee sobre fondo `#252540` |
| Titulo mes/anio en header | `.mantine-CalendarHeader-calendarHeaderLevel` | `color: #a0a0b0` | Contraste insuficiente, especialmente en la vista de seleccion |
| Botones de mes (vista meses) | `.mantine-MonthsList-monthsListControl` | `color: #c8c8d8` | Puede no aplicarse correctamente |
| Botones de anio (vista anios) | `.mantine-YearsList-yearsListControl` | `color: #c8c8d8` | Puede no aplicarse correctamente |
| Flechas de navegacion | `.mantine-CalendarHeader-calendarHeaderControl` | `color: #a0a0b0` | Contraste bajo |
| Dias de la semana (Lu, Ma...) | `.mantine-Month-monthThead th` | `color: #a0a0b0` | Contraste bajo |

### Donde se usa DatePickerInput

- `layouts/main_layout.py:67` — filtro de fechas del dashboard de ventas (`id='filtro-fechas'`)
- `layouts/tablero_layout.py:65` — filtro de fechas del tablero comparativo (`id='filtro-fechas'`)

Ambos usan `styles=dark_input_styles` que define `input.color: DARK['text']` (#ffffff), pero el CSS global puede estar sobreescribiendolo.

## Requisitos Funcionales

### RF-001: Valor del input legible con picker cerrado
**When** el DatePickerInput tiene un rango seleccionado y esta cerrado,
**Then** el texto del valor (ej: "01/03/2026 - 02/03/2026") debe ser blanco (#ffffff) sobre fondo `#252540`.

### RF-002: Titulo de mes/anio legible en header del calendario
**When** el calendario esta abierto mostrando la vista de dias,
**Then** el titulo central (ej: "Marzo 2026") debe ser blanco (#ffffff) o claro (#e8e8f0).

### RF-003: Botones de meses legibles en vista de meses
**When** el usuario hace click en el titulo del mes para ver la grilla de meses,
**Then** todos los nombres de meses deben ser claramente legibles (#e8e8f0) sobre fondo oscuro.

### RF-004: Botones de anios legibles en vista de anios
**When** el usuario hace click en el titulo del anio para ver la grilla de anios,
**Then** todos los numeros de anio deben ser claramente legibles (#e8e8f0) sobre fondo oscuro.

### RF-005: Flechas y controles de navegacion visibles
**When** el calendario esta abierto,
**Then** las flechas de navegacion (< >) y dias de la semana deben tener contraste suficiente (#c8c8d8 minimo).

### RF-006: Rango seleccionado visible en todas las vistas
**When** hay un rango seleccionado (dia, mes o anio en range mode),
**Then** los items `[data-in-range]` y `[data-selected]` deben tener fondo azul distinguible y texto blanco.

## Implementacion

Archivo unico: `assets/dark_theme.css`

### Cambios requeridos

1. **Agregar/reforzar** selector para el input value:
```css
.mantine-DatePickerInput-input {
    color: #ffffff !important;
    background-color: #252540 !important;
    border-color: #2d2d44 !important;
}
```

2. **Subir contraste** del header level (titulo mes/anio):
```css
.mantine-CalendarHeader-calendarHeaderLevel {
    color: #e8e8f0 !important;
}
```

3. **Subir contraste** de flechas de navegacion:
```css
.mantine-CalendarHeader-calendarHeaderControl {
    color: #c8c8d8 !important;
}
```

4. **Verificar/reforzar** botones de mes y anio con selectores mas especificos si no aplican.

5. **Verificar** `[data-in-range]` en vistas de meses/anios (no solo dias).

## Criterios de aceptacion

- [ ] El valor del rango se lee claramente con el picker cerrado
- [ ] Al abrir el calendario, el titulo "Marzo 2026" se lee claramente
- [ ] Al hacer click en el titulo, la grilla de meses se lee claramente
- [ ] Al hacer click en el anio, la grilla de anios se lee claramente
- [ ] Las flechas < > son visibles
- [ ] Los dias seleccionados y en rango se distinguen claramente
- [ ] No se rompen los estilos de otros componentes dmc
