---
name: poucenia
description: Kontrola a schválenie toho, čo sa Claude naučil – prejde automaticky naučené inštinkty od observera aj poučenia z aktuálnej práce, navrhne pravidlá na schválenie a schválené uloží natrvalo (projektové do repa projektu, globálne do pluginu). Použi na „/poucenia“, „čo si sa naučil“, „zapamätaj si to“, „ulož si to pravidlo“, alebo po tom, čo ťa používateľ opravil či sa vyriešila netriviálna chyba.
---

# Poučenia

Most medzi automatickým učením (observer na pozadí, model Haiku) a trvalými pravidlami.
Automaticky naučené inštinkty žijú lokálne v `ecc-homunculus` a v cloude by zanikli s kontajnerom.
Až schválením sa stanú trvalými a platia všade.

## Kde čo je

- **CLI na inštinkty:** `<plugin>/learning/scripts/instinct-cli.py`, kde `<plugin>` je adresár
  dve úrovne nad týmto skillom (base directory skillu → `../..`). Spúšťaj cez `python3`.
- **Automaticky naučené:** `python3 <cli> status` ich vypíše (projektové aj globálne). Súbory sú v
  `${XDG_DATA_HOME:-~/.local/share}/ecc-homunculus/projects/<hash>/instincts/personal/<id>.md`
  (projektové; `<hash>` je v hlavičke výstupu `status`) a v `…/ecc-homunculus/instincts/personal/` (globálne).
- **Schválené projektové:** `<koreň projektu>/.claude/instincts/<id>.md` – commitujú sa s projektom.
- **Schválené globálne:** `plugins/core/instincts/<id>.md` v repe `MatusBakala/claude-setup`.

## Postup

1. **Zber kandidátov**
   - `python3 <cli> status` – automaticky naučené inštinkty.
   - Z aktuálnej konverzácie: kde ťa používateľ opravil, čo bola netriviálna príčina chyby,
     čo bola slepá ulička, aký postup sa osvedčil. Len veci, ktoré sa budú **opakovať** – nie jednorazové fakty.
   - Preskoč kandidátov, ktorí už sú medzi schválenými (rovnaké alebo podobné `id` / význam).

2. **Návrh** – ukáž tabuľku, každý kandidát jeden riadok:

   | # | Pravidlo (keď … → urob …) | Rozsah | Confidence | Zdroj |
   |---|---------------------------|--------|------------|-------|

   Rozsah: **projekt** (konvencie, štruktúra, knižnice konkrétneho projektu) alebo **globálne**
   (všeobecné postupy, git, bezpečnosť, tvoje preferencie). Pri pochybnosti projekt.
   Pri každom automatickom inštinkte zhodnoť, či dáva zmysel – Haiku sa mýli; zlé navrhni zamietnuť.

3. **Rozhodnutie** – opýtaj sa: ktoré schváliť, ktoré upraviť, ktoré zamietnuť, prípadne zmeniť rozsah.
   Nič neukladaj bez odpovede.

4. **Uloženie schválených** – formát súboru (rovnaký ako ECC, aby fungovalo aj `/evolve`):

   ```markdown
   ---
   id: kebab-case-nazov
   trigger: when <konkrétna situácia>
   confidence: 0.8
   domain: code-style | testing | git | debugging | workflow | file-patterns | trading
   source: approved
   scope: project | global
   ---

   # Názov

   ## Action
   <čo robiť, jedna jasná veta>

   ## Evidence
   - <prečo – oprava od používateľa / chyba z <dátum>>
   ```

   - **Projekt:** zapíš do `<koreň projektu>/.claude/instincts/`. Commit spolu s ostatnými zmenami
     alebo samostatne (`chore: add learned instincts`) – podľa brány 2, hneď po schválení inštinktov.
   - **Globálne:** potrebuješ lokálnu kópiu repa `claude-setup`:
     1. Hľadaj v tomto poradí: `$CORE_SETUP_REPO`, `~/claude-setup`, `~/code/claude-setup`, `~/Projects/claude-setup`.
     2. Ak nie je, `git clone https://github.com/MatusBakala/claude-setup.git ~/claude-setup`.
     3. Zapíš do `plugins/core/instincts/<id>.md`, commitni hneď po schválení
        (`chore(instincts): add <id>`) a push.
     4. Ak klon alebo push nejde (napr. cloud session bez prístupu k repu), ulož súbor dočasne
        do projektu ako `.claude/instincts/<id>.md` so `scope: global` a povedz používateľovi,
        že ho treba presunúť do `claude-setup` (urobí to nabudúce `/poucenia` s prístupom).
     5. Pripomeň, že nová verzia pluginu sa načíta po `claude plugin marketplace update matus`
        a `claude plugin update core@matus` (na počítači) – v novej cloud session automaticky.

5. **Upratanie** – schválené a zamietnuté automatické inštinkty zmaž z `ecc-homunculus`
   (cesty pozri vyššie v „Kde čo je“), aby sa nezobrazovali dvakrát.

6. **Súhrn** – jeden riadok: koľko schválených (kam), upravených, zamietnutých.

## Údržba (občas)

Keď schválených inštinktov pribudne (zhruba 10+ v jednej oblasti), navrhni skill `instinkty`
→ `evolve`: zoskupí podobné do nového skillu alebo pravidla v `preferencie.md`.
