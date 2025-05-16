API docs for CrackNuts
======================

Commands
--------

API docs build commands.

i18n update
-----------
sphinx-build -b gettext source build/gettext
sphinx-intl update -p build\gettext -l zh_CN

build
-----
sphinx-build -b html source build\$(cracknuts --version)
sphinx-build -b html source build\$(cracknuts --version)\zh_CN -D language=zh_CN