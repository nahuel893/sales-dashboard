# Incidencias — Dark Theme & Buscador de Clientes

Fecha: 2026-02-21
Versión base: v1.1.0 (`6d8cba1`)

---

## INC-01: `html.Style` no existe en Dash

**Commit:** `03e50ca`
**Síntoma:** Error al iniciar la app: `AttributeError: module 'dash.html' has no attribute 'Style'`.
**Causa:** Se intentó usar `html.Style("""...""")` en `main_layout.py` para inyectar CSS inline del buscador. El componente `html.Style` no existe en Dash.
**Resolución:** Se movió el CSS a `assets/search_dropdown.css`. Dash carga automáticamente todos los archivos en `assets/`.
**Archivos:** `layouts/main_layout.py`, `assets/search_dropdown.css` (nuevo)

---

## INC-02: Falta de contraste general — colores hardcodeados en tema claro

**Commit:** `85ae953`
**Síntoma:** Múltiples componentes con fondos claros (`#f5f7fa`, `white`, `#f0f0f0`) y texto oscuro (`#333`, `#666`, `#999`) que no contrastan contra el tema oscuro del dashboard.
**Causa:** Las páginas `/clientes`, `/cliente/<id>` y sus callbacks usaban colores hardcodeados del tema claro original. Los `dcc.Dropdown` del YTD y los jump-to de `/cliente` no tenían estilos oscuros. Los componentes `dmc` (Chip, Slider, Switch, DatePicker, SegmentedControl) no tenían overrides para dark theme.
**Resolución:**
- Se creó `assets/dark_theme.css` (renombrado de `search_dropdown.css`) con CSS global para:
  - `dcc.Dropdown` (Dash 4.x): wrapper, search, options, selected, clear/arrow icons
  - `dmc` components: Combobox options, Chip, Slider, Switch, DatePicker, SegmentedControl, ScrollArea
  - Scrollbar global (webkit)
  - `dcc.Tabs` selected state
- Se migraron `clientes_layout.py` y `cliente_layout.py` al tema `DARK` (import + reemplazo de colores)
- Se corrigieron 14 colores en `cliente_callbacks.py` (header, badges, KPIs, tabla completa, botones Excel)
- Se corrigieron 5 colores en `clientes_callbacks.py` (tabla de resultados completa)
- Se corrigieron 3 colores en `ytd_callbacks.py` (estados N/A)
- Se actualizó el footer de `home_layout.py` (año 2025 → 2026)

**Archivos:** `assets/dark_theme.css`, `callbacks/cliente_callbacks.py`, `callbacks/clientes_callbacks.py`, `callbacks/ytd_callbacks.py`, `layouts/cliente_layout.py`, `layouts/clientes_layout.py`, `layouts/home_layout.py`

---

## INC-03: Buscador de clientes — sin contraste sobre el mapa

**Commit:** `85ae953`
**Síntoma:** El `dcc.Dropdown` del buscador de clientes aparecía con fondo blanco y texto oscuro sobre el mapa, haciéndolo ilegible.
**Causa:** Los selectores CSS globales (`.dash-dropdown-wrapper`, etc.) no eran suficientes para overridear los estilos por defecto de Dash 4. El dropdown carecía de un contenedor con fondo sólido.
**Resolución:**
- Se agregó fondo sólido `DARK['card']`, border-radius y box-shadow al div contenedor del overlay
- Se agregaron reglas CSS por ID (`#busqueda-cliente-mapa`) con selectores de atributo `[class*="..."]`
- Se aplicó el mismo tratamiento a los dropdowns de YTD y jump-to por ID

**Archivos:** `assets/dark_theme.css`, `layouts/main_layout.py`

---

## INC-04: Ítem seleccionado indistinguible del hover en MultiSelect

**Commits:** `a1b9373`, `f4d880f`
**Síntoma:** Al abrir un filtro MultiSelect en el drawer, el ítem bajo el mouse (hover) y el ítem ya seleccionado tenían colores casi idénticos — ambos azul oscuro, imposible distinguirlos.
**Causa:** Los estados `data-combobox-active` (hover) y `data-combobox-selected` usaban fondos `#2a3a5e` y `#1e3a6e` respectivamente — diferencia de apenas 12 unidades en el canal azul.
**Resolución en 2 pasos:**

1. **CSS** (`a1b9373`): Se diferenciaron visualmente los estados:
   - Hover: fondo sutil `#252545`
   - Seleccionado: fondo `#1a3060` + texto cyan `#5ab8f5` + borde izquierdo azul 3px
   - Seleccionado+hover: fondo `#1e3a70` + texto `#7dccff`

2. **Python** (`f4d880f`): Se pasó `backgroundColor` directamente via `comboboxProps.styles.option` en el layout, ya que Mantine aplicaba estilos inline que ganaban al CSS. Se creó `dark_combobox_props` centralizado y se reemplazaron los 10 `comboboxProps={"zIndex": 1100}` del drawer.

**Archivos:** `assets/dark_theme.css`, `layouts/main_layout.py`

---

## INC-05: Texto gris en el input de búsqueda del buscador de clientes

**Commits:** `ff9a220`, `443c36b`, `7ca8334`
**Síntoma:** Al tipear en el buscador de clientes sobre el mapa, el texto ingresado se veía gris claro sobre fondo blanco — ilegible.
**Causa:** El `dcc.Dropdown` de Dash 4 renderiza su panel desplegable (search input + opciones) como un **portal** fuera del DOM del componente. Los selectores CSS por ID (`#busqueda-cliente-mapa .dash-dropdown-search`) no alcanzaban estos elementos portalados. Además, el selector global `.dash-dropdown-search` tenía `background-color: transparent`, heredando el fondo blanco del portal.
**Resolución en 3 iteraciones:**

1. **Wildcard** (`ff9a220`): Se intentó `#busqueda-cliente-mapa *` como selector universal — no funcionó por el portal.
2. **Clases exactas por ID** (`443c36b`): Se usaron las clases confirmadas de Dash 4 (`.dash-dropdown-search`, `.dash-dropdown-placeholder`, etc.) scoped al ID — no funcionó por el portal.
3. **Selectores globales** (`7ca8334`): Se corrigió el selector global `.dash-dropdown-search` de `transparent` a `#1a1a2e` explícito, `color: #ffffff`, `caret-color: #ffffff`. Se agregó `.dash-dropdown-search-container` con fondo oscuro.

**Aprendizaje:** Los `dcc.Dropdown` de Dash 4 renderizan el panel desplegado en un portal al body. Cualquier estilo para elementos dentro del panel debe ser **global**, no scoped por ID del componente padre.

**Archivos:** `assets/dark_theme.css`

---

## Resumen de commits

| Commit | Tipo | Descripción |
|--------|------|-------------|
| `5d3d540` | feat | Buscador de clientes sobre mapa de burbujas |
| `03e50ca` | fix | INC-01: Mover CSS a assets (html.Style no existe) |
| `85ae953` | fix | INC-02 + INC-03: Dark theme global + contraste buscador |
| `a1b9373` | fix | INC-04a: Diferenciar selected vs hover en MultiSelect |
| `f4d880f` | fix | INC-04b: Forzar fondo oscuro via comboboxProps |
| `ff9a220` | fix | INC-05a: Wildcard selector para texto del input |
| `443c36b` | fix | INC-05b: Clases exactas de Dash 4 por ID |
| `7ca8334` | fix | INC-05c: Selector global para portal del dropdown |
