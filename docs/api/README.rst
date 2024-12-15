Generate markdown

构建markdown
sphinx-build -b markdown source build\$(cracknuts --version)

直接构建html
sphinx-build -b html source build\$(cracknuts --version)

生成后在文件头加入

---
toc_max_heading_level: 2
---