
class TournamentType(object):
    def draw_pairings(self, tournament, group):
        players = list(tournament.players)
        for i in range(0, len(players)-1, 2):
            params = {}
            params['Player 1'] = players[i]
            params['Player 2'] = players[i+1]
            params['Group'] = group
            params['Result'] = None
            tournament.pairings.append(params)

