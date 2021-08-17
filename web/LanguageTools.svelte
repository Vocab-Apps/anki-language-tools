<script context="module">
    import { writable } from 'svelte/store';
    export const currentlyLoadingStore = writable(false);    
    export function set_field_value(field_id, value) {
        var decoded_value = decodeURI(value);

        var field = getEditorField(field_id);
        field.editingArea.fieldHTML = decoded_value;
    }

    export function setCurrentlyLoading(loading) {
        currentlyLoadingStore.set(loading);
    }        
</script>


<script>
    
    let liveUpdates = true;
    let currentlyLoading = false;

    currentlyLoadingStore.subscribe(value => {
		currentlyLoading = value;
	});

    function toggleLiveUpdates() {
        liveUpdates = !liveUpdates;
        bridgeCommand('liveupdates:' + liveUpdates);
    }

</script>

<style>
.language-tools-block {
    display: flex;
    align-items: center;
    border-style: solid;
    border-width: 1px;
    border-color: #b6b6b6;
    border-radius: 3px;
    height: 28px;
    background-color: white;
    margin-top: 3px;    
}
.language-tools-loading {
    color: red;
}
div {
    padding-left: 5px;
    padding-right: 5px;
}
button {
    padding-top: 0px;
    padding-bottom: 0px;
    margin-left: 5px;
    margin-right: 5px;
}
</style>


<div class="language-tools-block">
    <div>
        <b>Language Tools</b>
    </div>
    <div>Live Updates: <b>{liveUpdates === true ? 'on' : 'off'}</b></div>
    {#if currentlyLoading} 
    <div class="language-tools-loading">Loading...</div>
    {:else}
    <button on:click={toggleLiveUpdates}>
        turn {liveUpdates === true ? 'off' : 'on'}
    </button>
    <button>run now</button>
    {/if}
</div>