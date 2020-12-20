#python imports
import json

# anki imports
import aqt
import aqt.gui_hooks
import aqt.editor
import aqt.webview

# addon imports
from .languagetools import DeckNoteTypeField, build_deck_note_type
from . import constants


def apply_inline_translation_changes(editor: aqt.editor.Editor, deck_note_type_field: DeckNoteTypeField, target_language):
    model = aqt.mw.col.models.get(deck_note_type_field.deck_note_type.model_id)
    fields = model['flds']
    field_names = [x['name'] for x in fields]
    field_index = field_names.index(deck_note_type_field.field_name)
    editor.web.eval(f"add_inline_field('{constants.EDITOR_WEB_FIELD_ID_TRANSLATION}', {field_index}, 'Translation')")

def init(languagetools):
    aqt.mw.addonManager.setWebExports(__name__, r".*(css|js)")

    def on_webview_will_set_content(web_content: aqt.webview.WebContent, context):
        if not isinstance(context, aqt.editor.Editor):
            return
        addon_package = aqt.mw.addonManager.addonFromModule(__name__)
        javascript_path = f"/_addons/{addon_package}/editor_javascript.js"
        web_content.js.insert(0,  javascript_path)

    def loadNote(editor: aqt.editor.Editor):
        note = editor.note

        model_id = note.mid
        card = editor.card
        deck_id = card.did        

        deck_note_type = build_deck_note_type(deck_id, model_id)

        inline_translations = languagetools.get_inline_translations(deck_note_type)

        for field_name, target_language in inline_translations.items():
            deck_note_type_field = DeckNoteTypeField(deck_note_type, field_name)
            apply_inline_translation_changes(editor, deck_note_type_field, target_language)

        # self.web.eval('add_inline_fields()')
        # editor.web.eval('add_inline_field(0)')

        # load inline translation using self.mw.taskman.run_in_background(self._check, self._on_finished)
        
        # self.web.eval(f"""set_html_src_fields()""")
        # flds = self.note.model()["flds"]
        # srcs = [fld.get("src remembered", False) for fld in flds]
        # self.web.eval(f"set_src_fields({json.dumps(srcs)});")

    def onBridge(handled, str, editor):
        return handled # don't do anything for now

        """Extends the js<->py bridge with our pycmd handler"""
        if not isinstance(editor, aqt.editor.Editor):
            return handled
        elif not str.startswith("src remembered"):
            return handled
        elif not editor.note:
            # shutdown
            return handled
        elif not getUserOption(keys="src remembered", default=False):
            return handled
        else:
            (cmd, ord, to) = str.split(":", 2)
            cur = int(ord)
            flds = editor.note.model()['flds']
            flds[cur]['src remembered'] = json.loads(to)
        return (True, None)

    aqt.gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    aqt.gui_hooks.editor_did_load_note.append(loadNote)
    aqt.gui_hooks.webview_did_receive_js_message.append(onBridge)
