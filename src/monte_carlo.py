"""
Monte Carlo simulation for tennis match outcomes
"""
import numpy as np


def simulate_point(server_first_in, server_first_win, server_second_win):
    """Simulate a single point"""
    if np.random.random() < server_first_in:
        return np.random.random() < server_first_win
    return np.random.random() < server_second_win


def simulate_game(server_first_in, server_first_win, server_second_win,
                  returner_first_in, returner_first_win, returner_second_win):
    """Simulate a single game"""
    server_score = 0
    returner_score = 0
    while True:
        if simulate_point(server_first_in, server_first_win, server_second_win):
            server_score += 1
        else:
            returner_score += 1
        if server_score >= 4 and server_score >= returner_score + 2:
            return True
        if returner_score >= 4 and returner_score >= server_score + 2:
            return False


def simulate_tiebreak(p1_first_in, p1_first_win, p1_second_win,
                      p2_first_in, p2_first_win, p2_second_win):
    """Simulate a tiebreak"""
    p1_score = 0
    p2_score = 0
    point_number = 0
    while True:
        point_number += 1
        if point_number == 1 or (point_number - 1) % 4 < 2:
            if simulate_point(p1_first_in, p1_first_win, p1_second_win):
                p1_score += 1
            else:
                p2_score += 1
        else:
            if simulate_point(p2_first_in, p2_first_win, p2_second_win):
                p2_score += 1
            else:
                p1_score += 1
        if p1_score >= 7 and p1_score >= p2_score + 2:
            return True
        if p2_score >= 7 and p2_score >= p1_score + 2:
            return False


def simulate_set(server_first_in, server_first_win, server_second_win,
                 returner_first_in, returner_first_win, returner_second_win):
    """Simulate a single set"""
    server_games = 0
    returner_games = 0
    server_serving = True
    while True:
        if server_serving:
            if simulate_game(server_first_in, server_first_win, server_second_win,
                             returner_first_in, returner_first_win, returner_second_win):
                server_games += 1
            else:
                returner_games += 1
        else:
            if simulate_game(returner_first_in, returner_first_win, returner_second_win,
                             server_first_in, server_first_win, server_second_win):
                returner_games += 1
            else:
                server_games += 1

        if server_games >= 6 and server_games >= returner_games + 2:
            return True
        if returner_games >= 6 and returner_games >= server_games + 2:
            return False
        if server_games == 6 and returner_games == 6:
            return simulate_tiebreak(server_first_in, server_first_win, server_second_win,
                                     returner_first_in, returner_first_win, returner_second_win)
        server_serving = not server_serving


def simulate_match(p1_first_in, p1_first_win, p1_second_win,
                   p2_first_in, p2_first_win, p2_second_win,
                   num_sets=5):
    """Simulate a complete match (best of 5 sets)"""
    p1_sets = 0
    p2_sets = 0
    sets_played = 0
    p1_serves_first = True
    while sets_played < num_sets and p1_sets < 3 and p2_sets < 3:
        if p1_serves_first:
            p1_wins_set = simulate_set(p1_first_in, p1_first_win, p1_second_win,
                                       p2_first_in, p2_first_win, p2_second_win)
        else:
            p1_wins_set = not simulate_set(p2_first_in, p2_first_win, p2_second_win,
                                           p1_first_in, p1_first_win, p1_second_win)
        if p1_wins_set:
            p1_sets += 1
        else:
            p2_sets += 1
        sets_played += 1
        p1_serves_first = not p1_serves_first
    return p1_sets == 3


def monte_carlo_simulation(p1_first_in, p1_first_win, p1_second_win,
                           p2_first_in, p2_first_win, p2_second_win,
                           num_simulations=10000):
    """
    Run Monte Carlo simulation to estimate win probability
    
    Args:
        p1_first_in: Player 1's first serve in percentage
        p1_first_win: Player 1's first serve win percentage
        p1_second_win: Player 1's second serve win percentage
        p2_first_in: Player 2's first serve in percentage
        p2_first_win: Player 2's first serve win percentage
        p2_second_win: Player 2's second serve win percentage
        num_simulations: Number of simulations to run
    
    Returns:
        Win probability for player 1
    """
    wins = 0
    for _ in range(num_simulations):
        if simulate_match(p1_first_in, p1_first_win, p1_second_win,
                          p2_first_in, p2_first_win, p2_second_win):
            wins += 1
    return wins / num_simulations
