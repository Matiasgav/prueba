#!/bin/sh
# Descarga los PDF oficiales de KG y las láminas de KHK usados por tools/capturas.py.
set -e
cd "$(dirname "$0")/../fuentes"
for u in \
  https://www.kggear.co.jp/wp-content/uploads/2022/11/KG4001WEB-7.pdf \
  https://www.kggear.co.jp/wp-content/uploads/2022/11/KG4001WEB-8.pdf \
  https://www.kggear.co.jp/wp-content/uploads/KG3001_web_0009.pdf \
  https://www.kggear.co.jp/wp-content/uploads/2024/06/KG5001JP_reference.pdf \
  https://www.kggear.co.jp/en/wp-content/themes/bizvektor-global-edition/pdf/TechnicalData_KGSTOCKGEARS.pdf
do curl -sSL -o "$(basename "$u")" "$u"; done
