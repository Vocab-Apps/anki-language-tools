<script>
    let liveUpdates = true;
    $: {
        if(bridgeCommand != undefined){
            bridgeCommand('liveupdates:' + liveUpdates);
        }
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
    <div>Live Updates: <b>on</b></div>
    <button>turn off</button>
    <button>run now</button>
</div>