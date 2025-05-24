// Funciones principales para la aplicación de monitoreo judicial

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Manejar cambios en el tipo de persona para ajustar la interfaz
    const tipoPersonaSelect = document.getElementById('tipo_persona');
    if (tipoPersonaSelect) {
        tipoPersonaSelect.addEventListener('change', function() {
            const nombreLabel = document.querySelector('label[for="nombre"]');
            if (this.value === 'jur') {
                nombreLabel.textContent = 'Razón Social';
            } else {
                nombreLabel.textContent = 'Nombre Completo';
            }
        });
    }

    // Validación de formularios
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Función para copiar al portapapeles
    const copyButtons = document.querySelectorAll('.btn-copy');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Cambiar el texto del botón temporalmente
                const originalText = this.textContent;
                this.textContent = '¡Copiado!';
                setTimeout(() => {
                    this.textContent = originalText;
                }, 2000);
            });
        });
    });

    // Resaltar filas de actuaciones según su clasificación
    const actuacionesRows = document.querySelectorAll('tr[data-urgencia]');
    actuacionesRows.forEach(row => {
        const urgencia = row.getAttribute('data-urgencia');
        if (urgencia) {
            row.classList.add(`actuacion-${urgencia.toLowerCase()}`);
        }
    });
});
