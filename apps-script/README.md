# Registro de leads y búsquedas

El buscador guarda en una planilla de Google:

- **Leads** — nombre y correo que el visitante deja (opcional) tras su primera búsqueda.
- **Busquedas** — cada búsqueda: consulta, clases de Niza, filtro de vigencia,
  si respondió la API o el modo demo, cuántos resultados hubo y la coincidencia más alta.
  Si el visitante ya dejó sus datos, la fila queda asociada a su correo.
- **Eventos** — otros eventos (por ejemplo, cuando alguien cierra el formulario sin dejar datos).

Planilla: **Markip Buscador — Leads y Búsquedas**
<https://docs.google.com/spreadsheets/d/146IMXHXVWPA2EHgF6nanorNG__7R_eiCseZdHnem4mk/edit>

Las hojas y sus encabezados se crean solos con el primer registro.

## Puesta en marcha (5 minutos)

1. Abre la planilla y ve a **Extensiones → Apps Script**.
2. Borra el contenido de `Código.gs` y pega el de [`Codigo.gs`](Codigo.gs). Guarda.
3. **Implementar → Nueva implementación → Aplicación web**:
   - *Ejecutar como*: **Yo (emilio@markip.cl)**
   - *Quién tiene acceso*: **Cualquier usuario**
   - Implementar → autoriza los permisos que pide.
4. Copia la URL que termina en `/exec`.
5. En [`index.html`](../index.html), pega esa URL en la constante `TRACK_URL`:

   ```js
   const TRACK_URL = "https://script.google.com/macros/s/AKfy…/exec";
   ```

6. Sube el cambio. Listo: cada búsqueda y cada lead quedan en la planilla.

Mientras `TRACK_URL` esté vacío, el buscador funciona igual pero no registra nada.

## Notas técnicas

- El POST se envía con `Content-Type: text/plain` a propósito: Apps Script no responde
  el preflight `OPTIONS` de CORS, y así el navegador lo trata como *simple request*.
- El registro nunca bloquea la interfaz: si falla la red o la URL, el error se ignora.
- Cada visitante recibe un id anónimo en `localStorage` (`mk_vid`) para poder unir sus
  búsquedas con el lead. No usa cookies ni rastreo entre sitios.
- El formulario aparece **una sola vez** por navegador, tras la primera búsqueda, y se
  puede cerrar sin dejar datos (`mk_lead_asked` en `localStorage`).

## Si cambias de opinión sobre Google Sheets

`TRACK_URL` es un único endpoint que recibe JSON por POST. Para migrar a otra base
(Supabase, Airtable, un endpoint de `markip-api`), basta con reemplazar esa URL por
una que acepte el mismo JSON: `{type, visitor_id, ts, email, nombre, page, ref, ua, …}`.
