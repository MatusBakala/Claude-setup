# Dlhý projekt – vlny a časti

Načítaj pri veľkej zmene alebo keď používateľ povie, že pokračujeme v pláne. Dopĺňa `SKILL.md`
(tabuľka modelov, zadanie pre agenta, review a brány platia ďalej).

## Plán

1. Prečítaj stav: `PLAN.md` (sekcia Stav), ADR, vetvu a otvorený PR.
2. Nový plán → `architect` (Opus high; brief s výslovným zoznamom súborov a sekcií dokumentácie,
   nie „prečítaj projekt“). Ulož ho do `PLAN.md` → **BRÁNA 1**.
3. Plán musí mať: rozhrania medzi časťami, vlny, pri každej časti súbory, ktoré vlastní, čo číta,
   test, náročnosť a commit; zvlášť zoznam spoločných súborov.

**Pravidlo vlny:** časť, ktorá potrebuje výsledok inej časti, patrí do ďalšej vlny. Časti v jednej
vlne nesmú upravovať ten istý súbor. Spoločné súbory (registrácia testov, zoznamy, index) upravuješ
ty pri spájaní.

## Vlna

1. **Skúšobná časť** – v prvej vlne (a vždy, keď sa mení spôsob práce) pošli najprv jednu časť.
   Pozri výsledok (commit, stat, testy) a až potom spusti ostatné.
2. **Paralelne 2–4 implementeri**, každý s `isolation: worktree` a s riadkom **Báza** v zadaní
   (worktree vzniká z hlavnej vetvy, bez bázy by nevidel predchádzajúce vlny). Jedna časť =
   sekvenčne v hlavnom checkoute, bez worktree.
3. Model a effort každej časti podľa jej náročnosti a náročnosti projektu z plánu (pravidlo
   „Effort implementera“ v `SKILL.md`). Ak sa ukáže, že projekt je ťažší, než plán odhadol,
   zmeň náročnosť projektu v `PLAN.md` a ďalšie časti posielaj na high.
4. **Spojenie** – každú časť zvlášť: `git cherry-pick --no-commit <commit>`, vyrieš spoločné súbory
   (ponechaj obe strany) a commitni ju s jej správou – časti ostanú samostatné commity (pozri inštinkt
   o worktree commitoch). Potom spusti **celú** sadu testov.
5. **Review vlny** – `code-reviewer` nad `<začiatok vlny>..HEAD`. Nálezy → implementer s tým
   istým rozsahom → review znova.
6. **Commit a push** podľa preferencií, potom aktualizuj sekciu Stav v `PLAN.md` a commitni ju.

Ak agent nahlási „hotovo“ bez commitu alebo s podozrivo malým výsledkom, nie je hotovo – zadaj
znova s odkazom na to, čo už v jeho worktree je.

## Stav v PLAN.md (odovzdávka)

Kontajner v cloude zaniká a práca prechádza medzi zariadeniami. `PLAN.md` preto vždy obsahuje:

```markdown
## Stav
- Vetva: feat/... · PR: #.. (alebo „zatiaľ nie“)
- Hotové: vlna 1 (časti 1.1–1.3, commit abc123)
- Rozpracované: časť 2.2 – BLOCKED: chýba rozhodnutie o formáte exportu
- Ďalší krok: vlna 2, časti 2.1 a 2.3 paralelne
- Rozhodnutia: <krátko, s odkazom na ADR>
```

Commitnutý stav je jediná odovzdávka – čo nie je v commite a v `PLAN.md`, ďalšia session nevie.

## Koniec vetvy

1. Finálne review podľa `SKILL.md` (Opus high len s pomenovaným spúšťačom, inak Sonnet medium;
   pri jednej vlne netreba).
2. `security-reviewer`, ak niektorá vlna zasiahla bezpečnostný spúšťač.
3. PR podľa preferencií; v `PLAN.md` označ vetvu ako hotovú.

## Čo nerobiť

- Neposielaj implementera „pozrieť sa do projektu“ – zadanie je jeho celý svet.
- Nespúšťaj viac ako 4 implementerov naraz; spájanie a review sa potom zahltia.
- Nepúšťaj ďalšiu vlnu, kým predchádzajúca nemá zelené testy a review.
- Nepoužívaj `git stash` v zdieľanom checkoute počas behu agentov.
