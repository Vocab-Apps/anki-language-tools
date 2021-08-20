<script>
    let liveUpdates = true;
    let typingDelay = 1250;

    function toggleLiveUpdates() {
        liveUpdates = !liveUpdates;
        bridgeCommand('languagetools:liveupdates:' + liveUpdates);
    }

    function typingDelayChange(event){
        const value = event.target.value;
        // console.log('typingDelayChange: ', value);
        const cmdString = 'languagetools:typingdelay:' + value;
        bridgeCommand(cmdString);
    }

    function triggerAllFieldUpdate() {
        forEditorField([], (field, _data) => {
            const field_id = field.editingArea.ord;
            const field_value = field.editingArea.fieldHTML;
            // console.log('field_id: ', field_id, ' field_value: ', field_value);
            const cmdString = 'languagetools:forcefieldupdate:' + field_id + ':' + field_value;
            bridgeCommand(cmdString);
    });
}    

</script>

<style>
.language-tools-block {
    display: flex;
    font-size: 12px;
    align-items: center;
    border-style: solid;
    border-width: 1px;
    border-color: #b6b6b6;
    border-radius: 3px;
    height: 28px;
    background-color: white;
    margin-top: 3px;    
}
div {
    padding-left: 5px;
    padding-right: 5px;
}
.live-updates-on {
    color: #00c853;
    font-weight: bold;
}
.live-updates-off {
    color: #757575;
    font-weight: bold;
}

</style>


<div class="language-tools-block">
    <div>
        <b>Language Tools</b>
    </div>
    <div>
        {#if liveUpdates} 
        <span class="live-updates-on">Live Updates: on</span>
        {:else}
        <span class="live-updates-off">Live Updates: off</span>
        {/if}
    </div>

    <button on:click={toggleLiveUpdates} class="lt-field-button">
        turn {liveUpdates === true ? 'off' : 'on'}
    </button>
    <button on:click={triggerAllFieldUpdate} class="lt-field-button">run now</button>
    <div>delay (ms):
        <input type=number bind:value={typingDelay} on:input={typingDelayChange} min=250 max=2500 step=250>
    </div>
</div>