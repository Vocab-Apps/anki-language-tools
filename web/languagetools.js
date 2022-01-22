// build using:
// npm run build

import LanguageTools, {setLanguageToolsEditorSettings} from "./LanguageTools.svelte";

$editorToolbar.then((editorToolbar) => {
    console.log(setLanguageToolsEditorSettings);
    editorToolbar.toolbar.insertGroup({component: LanguageTools, id: "languagetools"});
});
