# Valorant Esports Player Impact - Summer 2022 (Updated Spring 2023)
> Evaluating impact of players in VCT 2023 Americas League Playoffs


When playing or watching Valorant, one can recognize when a player impacts the outcome of the round, but how impactful were they? It's hard to evaluate by just looking at the main stats of Kills, Deaths, and Assists with no context of how game was played. Thus, this project aims to quantify a player's impact. Data is scraped from [rib.gg](https://www.rib.gg/) which is then used to train a Logistic Regression Model to quantify how much a play (limited to events like kills, ressurections, plants, and defuses) changed the outcome of the round. The included scraped data are from the opening VCT 2023 Americas League. The model is trained on the regular season data and then used to quantify players' impact during the Playoffs.

Idea from https://medium.com/@matbessa12/valorant-impact-value-giving-credit-where-credit-is-due-d2b4ca66f03d


<br/>

## Results

* Impact Scores:

  ![image](https://github.com/Renzjordan1/Valorant-Esports-Player-Impact/assets/38296706/aba8686b-902f-42b8-a9b6-9edd0606219b)
  

* Scraped Data example:
  
  ![image](https://github.com/Renzjordan1/Valorant-Esports-Player-Impact/assets/38296706/977cf89c-9884-4c42-be3d-b7277d76febf)






<br/>

## How to Run on your Local Machine 
Clone:

```sh
git clone https://github.com/Renzjordan1/Valorant-Esports-Player-Impact/
```

Run:

```
jupyter notebook
```
Open All_Players_ImpactModel.ipynb and explore





## Tech Stack

* Python (Data Science libraries: BeautifulSoup, Pandas, SKLearn)

