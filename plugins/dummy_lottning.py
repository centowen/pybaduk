
class TournamentType(object):
    def draw_pairings(self, tournament, group):
        players = list(tournament.players)
        for i in range(0, len(players)-1, 2):
            params = {}
            params['player1'] = players[i]
            params['player2'] = players[i+1]
            params['group'] = group
            tournament.pairings.append(params)

