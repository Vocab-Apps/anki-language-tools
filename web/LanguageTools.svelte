<script context="module">
    import { writable } from 'svelte/store';
    
    export const liveUpdatesEnabledStore = writable(false);
    export const typingDelayStore = writable(0);

    export function setLanguageToolsEditorSettings(liveUpdatesEnabled, typingDelay) {
        console.log('setLanguageToolsEditorSettings: ', liveUpdatesEnabled, typingDelay);
        liveUpdatesEnabledStore.set(liveUpdatesEnabled);
        typingDelayStore.set(typingDelay);
    }

</script>

<script>

    function toggleLiveUpdates() {
        $liveUpdatesEnabledStore = ! $liveUpdatesEnabledStore;
        bridgeCommand('languagetools:liveupdates:' + $liveUpdatesEnabledStore);
    }

    function typingDelayChange(event){
        const value = $typingDelayStore;
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
.rounded-corners {
    border-style: solid;
    border-width: 1px;
    border-color: #b6b6b6;
    border-radius: 3px;
}
.language-tools-block {
    display: inline-flex;
    flex-direction: row;
    flex-wrap: wrap;
    font-size: 12px;
    align-items: center;
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
.delay-input {
    height: 15px;
}

</style>


<div class="language-tools-block rounded-corners">
    <div>
        <b>Language Tools</b>
    </div>
    <div>
        {#if $liveUpdatesEnabledStore} 
        <span class="live-updates-on">Live Updates: on</span>
        {:else}
        <span class="live-updates-off">Live Updates: off</span>
        {/if}
    </div>

    <button on:click={toggleLiveUpdates} class="lt-field-button rounded-corners">
        turn {$liveUpdatesEnabledStore === true ? 'off' : 'on'}
    </button>
    <button on:click={triggerAllFieldUpdate} class="lt-field-button rounded-corners">run now</button>
    <div>delay (ms):
        <input class="delay-input" type=number bind:value={$typingDelayStore} on:input={typingDelayChange} min=250 max=4000 step=250>
    </div>
</div>