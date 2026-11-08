# Schválené globálne inštinkty

Sem ukladá skill `/poucenia` pravidlá, ktoré si schválil a platia vo všetkých projektoch.
Na začiatku každej session ich hook `session-context.py` vloží do kontextu.

Jeden súbor = jeden inštinkt (`<id>.md`). Formát je opísaný v `skills/poucenia/SKILL.md`.
Súbory môžeš kedykoľvek upraviť alebo zmazať aj ručne.

Osobné inštinkty (o používateľovi, nie o postupe práce) patria do `osobne/`. Priečinok je v
`.gitignore`, hook ich načíta, ale do gitu sa nedostanú.
