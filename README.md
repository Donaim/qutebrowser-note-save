This is a little plugin for [qutebrowser](https://github.com/qutebrowser/qutebrowser)

It add a `browser-note` command to qutebrowser that takes a note using currently selected text  
and then it invokes `my-browser-note-save` program to handle note text and related metadata (page title, date, page url, ..)

# HOWTO

`lib.py` file is intended to be imported to `config.py` file of qutebrowser's `basedir`/config folder

Example config.py:

```
# user's config

from importlib.machinery import SourceFileLoader
from os import path

SourceFileLoader('modulename', path.expanduser('~/devel/qutebrowser-note-save/lib.py')).load_module()
```

