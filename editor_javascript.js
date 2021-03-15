

function configure_languagetools_fields(options) {
    console.log(options);
    forEditorField(options, (field, field_type) => {
        const ord = field.editingArea.ord
         
        console.log(ord);
        console.log(field);
        console.log(field_type);

        if (!field.hasAttribute("has-languagetools")) {

            // add loading indicator
            const loadingIndicator = document.createElement('span');
            loadingIndicator.id = 'loading_indicator' + ord;
            loadingIndicator.classList.add('field-label-element');
            loadingIndicator.classList.add('loading-indicator');
            loadingIndicator.classList.add('loading-indicator-hidden');
            loadingIndicator.innerText = 'loading...';
            field.labelContainer.appendChild(loadingIndicator);

            // add generated for 
            const generatedForIndicator = document.createElement('span');
            generatedForIndicator.id = 'generatedfor_indicator' + ord;
            generatedForIndicator.classList.add('field-label-element');
            generatedForIndicator.classList.add('generated-for');
            generatedForIndicator.classList.add('generated-for-hidden');
            field.labelContainer.appendChild(generatedForIndicator);

            // do we need to add some audio buttons ?
            if( field_type == 'language') {
                const speakButton = document.createElement('button');
                speakButton.classList.add('field-label-element');
                speakButton.innerText = 'Speak';
                speakButton.addEventListener(
                    'click',
                    (() => {
                        pycmd('ttsspeak:' + ord)
                    }),
                );
                field.labelContainer.appendChild(speakButton);
            }

            if( field_type == 'sound') {
                const speakButton = document.createElement('button');
                speakButton.classList.add('field-label-element');
                speakButton.innerText = 'Play';
                speakButton.addEventListener(
                    'click',
                    (() => {
                        pycmd('playsoundcollection:' + ord)
                    }),
                );
                field.labelContainer.appendChild(speakButton);
            }            

            field.setAttribute("has-languagetools", "")
        }

    })    
}

function hide_loading_indicator(field_id, original_field_value) {
    $('#loading_indicator' + field_id).hide();
    $('#generatedfor_indicator' + field_id).text('generated from: ' + original_field_value);
    $('#generatedfor_indicator' + field_id).show();
}

function show_loading_indicator(field_id) {
    $('#loading_indicator' + field_id).show();
    $('#generatedfor_indicator' + field_id).hide();
}

function set_field_value(field_id, value) {
    var decoded_value = decodeURI(value);

    var field = getEditorField(field_id);
    console.log(field.editingArea);
    field.editingArea.fieldHTML = decoded_value;
}