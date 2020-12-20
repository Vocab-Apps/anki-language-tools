#python imports
import json

# anki imports
import aqt
import aqt.gui_hooks
import aqt.editor
import aqt.webview


def init(languagetools):
    aqt.mw.addonManager.setWebExports(__name__, r".*(css|js)")

    def on_webview_will_set_content(web_content: aqt.webview.WebContent, context):
        if not isinstance(context, aqt.editor.Editor):
            return
        addon_package = aqt.mw.addonManager.addonFromModule(__name__)
        javascript_path = f"/_addons/{addon_package}/editor_javascript.js"
        print(f'javascript_path: {javascript_path}')
        web_content.js.insert(0,  javascript_path)

    def loadNote(self):
        self.web.eval('add_inline_fields()')
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
