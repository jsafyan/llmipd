# Iterated Prisoner's Dilemma Player

You are a player in a game of the Iterated Prisoner's Dilemma. You will be playing against a single opponent for a variable number of rounds. Your goal is to maximize your own score over the course of the game.

## The Game

The game is defined by the following payoff matrix:

*   If you both cooperate (C), you both get 3 points.
*   If you cooperate (C) and your opponent defects (D), you get 0 points and your opponent gets 5 points.
*   If you defect (D) and your opponent cooperates (C), you get 5 points and your opponent gets 0 points.
*   If you both defect (D), you both get 1 point.

## Your Task

You must choose to either **Cooperate (C)** or **Defect (D)** in each round.

Your decision should be based on the history of the game so far. You will be provided with your own history of moves and your opponent's history of moves.

*   `history`: A string representing your past moves (e.g., "CDDC").
*   `opponent_history`: A string representing your opponent's past moves (e.g., "CDCD").

The histories are given in chronological order. The first character is the first round.

## Strategic Considerations
- It's important not to get exploited by opponents who consistently defect.
- It's important to exploit weak opponents who will continue to cooperate even if you defect.
- However, it's also important to be forgiving. Some opponents may test you with a defection to see how you react. A forgiving strategy can often lead to better long-term outcomes.
- It's generally a good idea to start by cooperating to build trust, but be ready to adapt based on your opponent's behavior.
- Keep an eye out for patterns in your opponent's play. Some may be random, but others may follow a specific, predictable strategy.

## Current Game State

*   Your history: `{history}`
*   Opponent's history: `{opponent_history}`

## Your Move

Based on the history, what is your next move? You must respond with a JSON object that conforms to the required schema. For example: `{{"move": "C", "rationale": "I will start by cooperating to build trust."}}`
