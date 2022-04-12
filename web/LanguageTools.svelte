<script context="module">
    import { writable } from 'svelte/store';
    
    export const liveUpdatesEnabledStore = writable(false);
    export const typingDelayStore = writable(0);
    export const updateLoading = writable(false);
    export const updatingFieldName = writable('');

    export function setLanguageToolsEditorSettings(liveUpdatesEnabled, typingDelay) {
        console.log('setLanguageToolsEditorSettings: ', liveUpdatesEnabled, typingDelay);
        liveUpdatesEnabledStore.set(liveUpdatesEnabled);
        typingDelayStore.set(typingDelay);
    }

    export function showLoadingIndicator(fieldName) {
        console.log('showLoadingIndicator: ', fieldName);
        updateLoading.set(true);
        updatingFieldName.set(fieldName);
    }

    export function hideLoadingIndicator(fieldName) {
        console.log('hideLoadingIndicator: ', fieldName);
        updateLoading.set(false);
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
        const cmdString = 'languagetools:fullupdate';
        bridgeCommand(cmdString);
    }

    function toggleComponentExpanded() {
        if( componentExpanded == false ) {
            componentExpanded = true;
        } else {
            componentExpanded = false;
        }
    }

    let componentExpanded = false;

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
.cursor-pointer {
    cursor: pointer;
}
.updating {
    color: #00c853;
    animation-name: stretch;
    animation-duration: 0.5s;
    animation-timing-function: ease-out;
    animation-direction: alternate;
    animation-iteration-count: infinite;
    animation-play-state: running;
}
@keyframes stretch {
    0% {
        opacity: 0.0;
    }

    50% {
    }

    100% {
        opacity: 1.0;
    }
}
</style>


<div class="language-tools-block rounded-corners">
    {#if $updateLoading} 
    <div on:click={toggleComponentExpanded} class="updating cursor-pointer">
        <b>Updating {$updatingFieldName}</b> 
    </div>
    {:else if $liveUpdatesEnabledStore}
    <div on:click={toggleComponentExpanded} class="cursor-pointer">
        <b>Language Tools</b> 
    </div>    
    {:else}
    <div on:click={toggleComponentExpanded} class="live-updates-off cursor-pointer">
        <b>Language Tools</b> 
    </div>
    {/if}

    {#if componentExpanded}
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
    {/if}
</div>