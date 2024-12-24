Generate markdown
=================

构建markdown
sphinx-build -b markdown source build\$(cracknuts --version)

直接构建html
sphinx-build -b html source build\$(cracknuts --version)
sphinx-build -b html source build\$(cracknuts --version)\zh_CN -D language=zh_CN

生成后在文件头加入

---
toc_max_heading_level: 2
---

国际化
sphinx-build -b gettext source build/gettext
sphinx-intl update -p build\gettext -l zh_CN