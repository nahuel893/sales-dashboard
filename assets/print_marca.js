/**
 * Event delegation para botones de Imprimir y Descargar PNG
 * en el detalle de cliente (accordion por marca).
 */
document.addEventListener('click', function(e) {
    var btn = e.target.closest('.btn-imprimir-marca, .btn-descargar-marca');
    if (!btn) return;

    var generico = btn.getAttribute('data-generico') || '';
    var marca = btn.getAttribute('data-marca') || '';

    // Buscar el contenedor de la tabla hermano
    var panel = btn.closest('.mantine-Accordion-panel');
    if (!panel) return;
    var contenido = panel.querySelector('.tabla-marca-content');
    if (!contenido) return;

    // Obtener nombre del cliente del header
    var headerEl = document.querySelector('#cliente-header-content h1');
    var cliente = headerEl ? headerEl.textContent.trim() : '';

    var titulo = generico + ' — ' + marca;

    if (btn.classList.contains('btn-imprimir-marca')) {
        // === IMPRIMIR ===
        var printWin = window.open('', '_blank', 'width=900,height=600');
        printWin.document.write(
            '<html><head><title>' + titulo + '</title>' +
            '<style>' +
            'body { font-family: Arial, sans-serif; padding: 20px; margin: 0; }' +
            'h2 { margin: 0 0 4px 0; font-size: 18px; }' +
            'h3 { margin: 0 0 12px 0; color: #666; font-size: 14px; font-weight: normal; }' +
            'table { width: 100%; border-collapse: collapse; }' +
            'th, td { padding: 6px 10px; border: 1px solid #ccc; font-size: 11px; }' +
            'th { background-color: #f0f0f0; font-weight: bold; }' +
            '</style></head><body>'
        );
        printWin.document.write('<h2>' + titulo + '</h2>');
        if (cliente) printWin.document.write('<h3>' + cliente + '</h3>');
        printWin.document.write(contenido.innerHTML);
        printWin.document.write('</body></html>');
        printWin.document.close();
        printWin.focus();
        printWin.print();

    } else if (btn.classList.contains('btn-descargar-marca')) {
        // === DESCARGAR PNG ===
        if (typeof html2canvas === 'undefined') {
            alert('html2canvas no cargado. Intente recargar la pagina.');
            return;
        }
        btn.textContent = 'Generando...';
        btn.disabled = true;

        html2canvas(contenido, {
            backgroundColor: '#ffffff',
            scale: 2,
            logging: false,
        }).then(function(canvas) {
            var link = document.createElement('a');
            link.download = (generico + '_' + marca).replace(/\s+/g, '_') + '.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
            btn.textContent = 'Descargar PNG';
            btn.disabled = false;
        }).catch(function() {
            alert('Error al generar la imagen.');
            btn.textContent = 'Descargar PNG';
            btn.disabled = false;
        });
    }
});
