// build using:
// yarn build

import * as NoteEditor from "anki/NoteEditor";
import LanguageTools, {setLanguageToolsEditorSettings} from "./LanguageTools.svelte";

NoteEditor.lifecycle.onMount(({ toolbar }) => {
    toolbar.toolbar.append({component: LanguageTools, id: "languagetools"});
});

window.setLanguageToolsEditorSettings = setLanguageToolsEditorSettings;