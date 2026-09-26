/**
 * Markip Buscador — registro de leads y búsquedas en Google Sheets.
 *
 * Recibe POST desde index.html (Content-Type: text/plain para evitar el
 * preflight CORS, que Apps Script no responde) y escribe una fila por evento.
 *
 * Instalación: ver apps-script/README.md
 */

// ID de la planilla "Markip Buscador — Leads y Búsquedas"
var SHEET_ID = '146IMXHXVWPA2EHgF6nanorNG__7R_eiCseZdHnem4mk';

var HEADERS = {
  'Leads': ['Fecha', 'Nombre', 'Correo', 'Primera búsqueda', 'Visitante', 'Página', 'Referente', 'Navegador'],
  'Busquedas': ['Fecha', 'Consulta', 'Clases', 'Vigencia', 'Fuente', 'Resultados',
                'Top coincidencia', 'Top %', 'Correo', 'Nombre', 'Visitante', 'Página', 'Referente', 'Navegador',
                'Algoritmo', 'Núcleo', 'Top 5'],
  'Eventos': ['Fecha', 'Tipo', 'Correo', 'Visitante', 'Página', 'Referente', 'Navegador', 'Detalle']
};

function doPost(e) {
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var now = new Date();

    if (d.type === 'lead') {
      append_('Leads', [now, d.nombre || '', d.email || '', d.primera_busqueda || '',
                        d.visitor_id || '', d.page || '', d.ref || '', d.ua || '']);
    } else if (d.type === 'search') {
      append_('Busquedas', [now, d.consulta || '', d.clases || '', d.vigencia || '',
                            d.fuente || '', d.n_resultados, d.top_marca || '', d.top_score,
                            d.email || '', d.nombre || '', d.visitor_id || '',
                            d.page || '', d.ref || '', d.ua || '',
                            d.algo || '', d.nucleo || '', d.top5 || '']);
    } else {
      append_('Eventos', [now, d.type || '', d.email || '', d.visitor_id || '',
                          d.page || '', d.ref || '', d.ua || '', d.detalle || '']);
    }
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function doGet() {
  return json_({ ok: true, service: 'markip-buscador-tracker' });
}

/** Agrega una fila, creando la hoja y sus encabezados si no existen. */
function append_(name, row) {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
  }
  var h = HEADERS[name];
  if (sh.getLastRow() === 0) {
    sh.appendRow(h);
    sh.getRange(1, 1, 1, h.length).setFontWeight('bold').setBackground('#EEF0FB');
    sh.setFrozenRows(1);
  } else if (sh.getLastColumn() < h.length) {
    // columnas nuevas (p.ej. Algoritmo, Núcleo, Top 5): se agregan al final sin tocar las filas existentes
    sh.getRange(1, sh.getLastColumn() + 1, 1, h.length - sh.getLastColumn())
      .setValues([h.slice(sh.getLastColumn())]).setFontWeight('bold').setBackground('#EEF0FB');
  }
  sh.appendRow(row);
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
