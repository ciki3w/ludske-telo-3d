# Ľudské telo 3D

Interaktívny anatomický 3D model ľudského tela na biológiu (ZŠ / SŠ).

**Spustiť:** https://ciki3w.github.io/ludske-telo-3d/

- skutočné anatomické modely orgánov, kostí, svalov, ciev a nervov
- otáčanie, zväčšovanie, zobrazenie/skrytie 10 sústav orgánov a jednotlivých orgánov
- kliknutím na orgán sa zobrazí zväčšený s popisom, funkciou a zaujímavosťou
- mozog rozdelený na laloky (čelový, temenný, spánkový, záhlavový), mozgové komory, limbický systém
- priehľadnosť kože, rez telom, popisky, vyhľadávanie
- kvízy „Nájdi orgán v tele“ a „Čo robí tento orgán?“

## Súbory
- `index.html` – aplikácia (Three.js z CDN, potrebuje internet)
- `telo.bin`, `telo.json` – zjednodušené 3D modely orgánov (~10 MB)
- `tools/build_model.py` – skript, ktorý balík vytvorí z dát BodyParts3D

Aplikáciu treba otvárať cez webový server (napr. GitHub Pages). Pri otvorení dvojklikom na `index.html` prehliadač nedovolí načítať model.

## Zdroj 3D dát a licencia
3D modely pochádzajú z databázy **BodyParts3D**, © The Database Center for Life Science (DBCLS),
licencia [Creative Commons Attribution-Share Alike 2.1 Japan](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en).
Súbory `telo.bin` a `telo.json` sú upravené (zjednodušené, zlúčené) odvodené dielo a šíria sa pod rovnakou licenciou.
Povrch pľúc a štítna žľaza sú v modeli dopočítané, pretože v BodyParts3D chýbajú.
https://dbarchive.biosciencedbc.jp/en/bodyparts3d/
