# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json

class SnakeGame(gl.Contract):
    scores:      TreeMap[Address, u256]
    high_scores: TreeMap[Address, u256]
    rewards:     TreeMap[Address, u256]
    taunts:      TreeMap[Address, str]

    def __init__(self):
        self.daily_seed = "genesis"

    @gl.public.write
    def submit_score(self, final_score: u256):
        player = gl.message.sender_address

        # Mise à jour scores
        current = self.scores.get(player, u256(0))
        if final_score > current:
            self.scores[player] = final_score

        high = self.high_scores.get(player, u256(0))
        if final_score > high:
            self.high_scores[player] = final_score

        # LLM TAUNT comme dans GenFlappy (feature obligatoire)
        def generate_taunt() -> str:
            prompt = f"Tu es un game master fun et sarcastique pour Snake. Le joueur a fait {int(final_score)} points. Réponds avec UNE phrase courte et drôle (max 12 mots)."
            return gl.nondet.exec_prompt(prompt).strip()[:120]

        taunt = gl.eq_principle.strict_eq(generate_taunt)
        self.taunts[player] = taunt

    @gl.public.write
    def claim_reward(self):
        player = gl.message.sender_address
        score = self.scores.get(player, u256(0))
        if score >= u256(5):
            self.rewards[player] = score * u256(10)

    @gl.public.view
    def get_player_data(self, player_str: str):
        player = Address(player_str)
        return {
            "score": int(self.scores.get(player, u256(0))),
            "high_score": int(self.high_scores.get(player, u256(0))),
            "reward": int(self.rewards.get(player, u256(0))),
            "taunt": self.taunts.get(player, "Joue pour avoir ton taunt AI !")
        }
