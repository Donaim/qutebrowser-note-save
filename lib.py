
from qutebrowser.commands import userscripts, runners
from qutebrowser.api import cmdutils
from qutebrowser.utils import (message, usertypes, log, qtutils, urlutils,
                               objreg, utils, standarddir, debug)
from os import path
import subprocess
import json

@cmdutils.register(instance='command-dispatcher', scope='window')
@cmdutils.argument('promptKeywords', choices=['True', 'False'])
def browser_note(self, promptKeywords, quiet=False):
	''' Makes a note using current selection (may be none)'''

	title = self._tabbed_browser.widget.page_title(self._current_index())
	url = self._yank_url('url')
	basedir = path.dirname(standarddir.config())

	def _question_callback(keywords):
		def _selection_callback(text):
			if not text and not quiet:
				message.info("Nothing selected")

			output = {
					'title': title,
					'url': url,
					'profile': basedir,
					'keywords': keywords,
					'text': text,
					}
			output = json.dumps(output)

			retcode = subprocess.call(['my-browser-note-save', output])
			if retcode != 0:
				message.error(f'Note subprocess failed with: {retcode}')

		caret = self._current_widget().caret
		caret.selection(callback=_selection_callback)

	if promptKeywords == 'True':
		message.ask_async(
			"Add note:",
			usertypes.PromptMode.text,
			_question_callback,
			text="Keywords: ")
	else:
		_question_callback(None)

