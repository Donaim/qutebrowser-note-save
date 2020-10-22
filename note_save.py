
from PyQt5.QtCore import QTimer
from qutebrowser.browser import downloads
from qutebrowser.commands import userscripts, runners
from qutebrowser.api import cmdutils
from qutebrowser.utils import (message, usertypes, log, qtutils, urlutils,
                               objreg, utils, standarddir, debug)
from qutebrowser.misc import objects

import os, json, tempfile, datetime, random, shutil
from os import path
from datetime import datetime

# Constants
notefile = path.expanduser('~/Documents/browser-notes.md')
notedir = path.expanduser('~/Documents/browser-note-pages')

# Helpers
def get_random_string(length):
    return ''.join(random.choice('123456789abcdef') for i in range(length))

def collect_keys(keywords_text):
	buf = []
	if not keywords_text: return ''

	for w in keywords_text.split(' '):
		if w.startswith('#'):
			if buf:
				yield ' '.join(buf)
				buf = []
			yield w
		else:
			buf.append(w)

	if buf: yield ' '.join(buf)

def main_json(data):
	# Initial info
	title = data['title']
	keywords = data['keywords']
	url = data['url']
	profile = data['profile']
	text = data['text']
	mhtml = data['mhtml']

	# Additional info
	time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	if mhtml:
		if not os.path.exists(notedir): os.mkdirs(notedir)
		dest_mhtml = path.join(notedir, get_random_string(8) + '.mhtml')
	else:
		dest_mhtml = ""

	# Preparation
	title = title.replace('\n', ' ')
	text = text.strip()
	if text: text = '```\n' + text + '\n```\n'

	keywords = collect_keys(keywords)
	keywords = ' '.join([''] + ['`' + k + '`' for k in keywords])

	# Output
	if mhtml: shutil.move(mhtml, dest_mhtml)

	with open(notefile, 'a+') as w:
		w.write(f'''
# {title}
- keywords:{keywords}
- time: `{time}`
- [url]({url})
- profile: `{profile}`
- [mhtml](file://{dest_mhtml})
{text}''')

@cmdutils.register(instance='command-dispatcher', scope='window', overwrite=True)
@cmdutils.argument('promptKeywords', choices=['True', 'False'])
def browser_note(self, promptKeywords, quiet=False):
	''' Makes a note using current selection (may be none)'''

	title = self._tabbed_browser.widget.page_title(self._current_index())
	url = self._yank_url('url')
	basedir = path.dirname(standarddir.config())

	download_manager = None
	download_dest = None
	downs = None
	def downloaded():
		if download_dest:
			basename = os.path.basename(download_dest)
			return [x for x in downs if x.done and x.basename == basename]
		else:
			return True

	try:
		tab = self._current_widget()
		downs = objreg.last_visible_window()._download_model
		download_manager = objreg.get('webengine-download-manager')
		download_dest = '/tmp/' + get_random_string(8) + '.html'
		target = downloads.FileDownloadTarget(download_dest)
		download_manager.get_mhtml(tab, target)
	except Exception as ex:
		downs = None
		download_dest = None
		download_manager = None
		message.error(f'Could not download the page: {ex}')

	def question_callback(keywords):
		def selection_callback(text):
			if not text and not quiet:
				message.info("Nothing selected")

			data = {
					'title': title,
					'url': url,
					'profile': basedir,
					'keywords': keywords,
					'text': text,
					'mhtml': download_dest or "",
				}

			def finish():
				try: main_json(data)
				except Exception as ex:
					message.error(f'Note subtask failed with: {ex}')

			def download_timer_callback(*args, **kwargs):
				items = downloaded()
				if items:
					download_timer.stop()
					for i in items: i.remove()
					finish()

			if downs:
				download_timer = None
				download_timer = QTimer()
				download_timer.setInterval(100)
				download_timer.timeout.connect(download_timer_callback)
				download_timer.start()
			else:
				finish()

		caret = self._current_widget().caret
		caret.selection(callback=selection_callback)

	if promptKeywords == 'True':
		message.ask_async(
			"Add note:",
			usertypes.PromptMode.text,
			question_callback,
			text="Keywords: ")
	else:
		question_callback(None)

