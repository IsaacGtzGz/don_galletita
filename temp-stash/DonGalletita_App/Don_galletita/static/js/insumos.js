document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('insumos-container');
    const addButton = document.querySelector('.btn-add-insumo');
    const totalForms = document.getElementById('id_insumos-TOTAL_FORMS');
    const emptyFormTemplate = document.getElementById('empty-insumo-form').innerHTML;
    
    let formCount = parseInt(totalForms.value);

    // Función para actualizar nombres e IDs
    function updateFormIndex(formElement, index) {
        const inputs = formElement.querySelectorAll('input, select, textarea, label');
        inputs.forEach(input => {
            if (input.tagName === 'LABEL') {
                if (input.htmlFor) {
                    input.htmlFor = input.htmlFor.replace(/insumos-\d+/, insumos-$,{index});
                }
            } else {
                if (input.id) input.id = input.id.replace(/insumos-\d+/, insumos-$,{index});
                if (input.name) input.name = input.name.replace(/insumos-\d+/, insumos-$,{index});
            }
        });
    }

    // Agregar nuevo formulario
    addButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        const newFormHtml = emptyFormTemplate.replace(/_prefix_/g, formCount);
        const newFormElement = document.createElement('div');
        newFormElement.innerHTML = newFormHtml;
        container.appendChild(newFormElement.firstElementChild);
        
        formCount++;
        totalForms.value = formCount;
    });

    // Eliminar formulario
    container.addEventListener('click', function(e) {
        if (e.target.closest('.btn-remove-insumo')) {
            e.preventDefault();
            const formToRemove = e.target.closest('.card-insumo');
            const forms = container.querySelectorAll('.card-insumo');
            
            if (forms.length > 1) {
                // Si es un formulario existente (con ID), marcamos para borrado
                const deleteInput = formToRemove.querySelector('input[name*="-DELETE"]');
                if (deleteInput) {
                    deleteInput.value = 'on';
                    formToRemove.style.display = 'none';
                } else {
                    // Si es un formulario nuevo, lo eliminamos directamente
                    formToRemove.remove();
                    formCount--;
                    totalForms.value = formCount;
                    
                    // Reindexar los formularios restantes
                    container.querySelectorAll('.card-insumo').forEach((form, index) => {
                        updateFormIndex(form, index);
                    });
                }
            }
        }
    });
});