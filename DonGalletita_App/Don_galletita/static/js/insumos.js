document.addEventListener('DOMContentLoaded', function() {
    // Función para actualizar la unidad de medida
    function updateUnidadMedida(selectElement) {
        // Encuentra el contenedor del formulario actual
        const formContainer = selectElement.closest('.card-insumo');
        // Encuentra el campo de unidad de medida
        const unidadInput = formContainer.querySelector('input[name$="-unidad_medida"]');
        
        // Obtiene la opción seleccionada
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        
        // Actualiza el valor si hay una opción seleccionada
        if (selectedOption && selectedOption.value) {
            // Usamos dataset.unidad que viene del data-unidad en el option
            unidadInput.value = selectedOption.dataset.unidad || '';
        } else {
            unidadInput.value = '';
        }
    }
  
    // Manejar cambios en los selects existentes
    document.addEventListener('change', function(event) {
        if (event.target.matches('select[name$="-insumo"]')) {
            updateUnidadMedida(event.target);
        }
    });

    const container = document.getElementById('insumos-container');
    const addButton = document.querySelector('.btn-add-insumo');
    const totalForms = document.getElementById('id_insumos-TOTAL_FORMS');
    const emptyFormElement = document.getElementById('empty-insumo-form');
    
    // Verificar que todos los elementos requeridos existen
    if (!emptyFormElement || !container || !addButton || !totalForms) {
        console.warn('Elementos del formulario de insumos no encontrados');
        return;
    }

    const emptyFormTemplate = emptyFormElement.innerHTML;
    let formCount = parseInt(totalForms.value);

    // Agregar nuevo formulario
    addButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, formCount);
        const newFormElement = document.createElement('div');
        newFormElement.innerHTML = newFormHtml;
        container.appendChild(newFormElement.firstElementChild);
        
        formCount++;
        totalForms.value = formCount;

        // Habilitar botón de eliminar
        const newForm = container.lastElementChild;
        const deleteButton = newForm.querySelector('.btn-remove-insumo');
        deleteButton.addEventListener('click', function() {
            handleDeleteForm(this);
        });
    });

    // Manejar eliminación de formularios
    container.addEventListener('click', function(e) {
        if (e.target.closest('.btn-remove-insumo')) {
            e.preventDefault();
            handleDeleteForm(e.target.closest('.btn-remove-insumo'));
        }
    });

    function handleDeleteForm(deleteButton) {
        const formCard = deleteButton.closest('.card-insumo');
        const deleteInput = formCard.querySelector('.delete-input');
        const formIdInput = formCard.querySelector('[id$="-id"]');
        
        if (formIdInput && formIdInput.value) {
            // Es un insumo existente - marcar para borrado
            deleteInput.value = 'on';
            formCard.style.opacity = '0.5';
            formCard.style.backgroundColor = '#ffebee';
            deleteButton.style.display = 'none';
        } else {
            // Es un nuevo insumo - eliminar completamente
            formCard.remove();
            formCount--;
            totalForms.value = formCount;
        }
    }
});