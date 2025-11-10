# Champions League Data Analysis

This note summarizes the Champions League match data and club ranking data provided for a prediction game.

## Champions League Match Data (Example Structure)

The data provided includes match results for Quarter-Finals, 1/8-Finals, and Group Stage rounds (Round 1 to Round 6).

**Example Format:**

```
DATE. TIME
Home Team
Away Team
Home Score
Away Score
(Half-time Home Score)
(Half-time Away Score)
```

**Example Match:**

```
12.04. 19:00
AC Milan
Napoli
1
0
(1)
(0)
```

## All-Time Ranking Club Data (CSV Format)

The data provides an all-time ranking of football clubs with various statistics.

**Columns:**

-   `Position`: Club's rank.
-   `Club`: Club name.
-   `Country`: Country of origin.
-   `Participated`: Number of times participated in the tournament.
-   `Titles`: Number of titles won.
-   `Played`: Number of games played.
-   `Win`: Number of games won.
-   `Draw`: Number of games drawn.
-   `Loss`: Number of games lost.
-   `Goals For`: Total goals scored.
-   `Goals Against`: Total goals conceded.
-   `Pts`: Total points earned (3 for win, 1 for draw).
-   `Goal Diff`: Goal difference.

**Example Row:**

```csv
1,Real Madrid CF,ESP,52,14,464,277,79,108,1021,508,633.0,513.0
```

## Organizing Data for a Prediction Game

1.  **Storage:** Use a spreadsheet or database.
2.  **Structure:** Separate data into columns for each category.
3.  **Prediction Questions (Examples):**
    -   Which club has the most titles?
    -   Which club has the best goal difference?
    -   Which club has the most points?
    -   Which club has the most played games?
    -   Which club has the highest win rate?
    -   Which club has the best win-loss ratio?
    -   Which club has the best goals for rate?
    -   Which club has the best goals against rate?
    -   Which club has the best win-draw ratio?

## Related Documents

- [[30-All-Notes/Entertainment_Recommendations..md]]
