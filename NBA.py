import sys
import pandas as pd

games = []
team_one = {}
team_two = {}
team_one_off = {}
team_one_def = {}
team_two_off = {}
team_two_def = {}
on_court1 = []
on_court2 = []
ft1 = []
ft2 = []
team_oneID = 'A'
team_twoID = 'B'
period = 1
possession = 'S'

pbp = pd.read_csv("Play_by_Play.txt", sep="\t")
ecodes = pd.read_csv("Event_Codes.txt", sep="\t")
lineup = pd.read_csv("Game_Lineup.txt", sep='\t')


def count_game():
    global games
    for row in pbp.itertuples():
        if row.Game_id not in games:
            games.append(row.Game_id)


def initialize(gameID):
    global team_oneID
    global team_twoID

    game = lineup[(lineup.Game_id == gameID) & (lineup.Period == 0)]
    for row in game.itertuples():
        if team_oneID == 'A' or row.Team_id == team_oneID:
            team_one[row.Person_id] = [0, 0]
            team_one_off[row.Person_id] = [0, 0]
            team_one_def[row.Person_id] = [0, 0]
            team_oneID = row.Team_id
        else:
            team_two[row.Person_id] = [0, 0]
            team_two_off[row.Person_id] = [0, 0]
            team_two_def[row.Person_id] = [0, 0]
            team_twoID = row.Team_id
    on_court = lineup[(lineup.Game_id == gameID) & (lineup.Period == 1)]
    for row in on_court.itertuples():
        if row.Team_id == team_oneID:
            on_court1.append(row.Person_id)
        else:
            on_court2.append(row.Person_id)


def change_lineup(gameID, temp):
    current = lineup[(lineup.Game_id == gameID) & (lineup.Period == temp)]
    del on_court1[:]
    del on_court2[:]
    for row in current.itertuples():
        if row.Team_id == team_oneID:
            on_court1.append(row.Person_id)
        else:
            on_court2.append(row.Person_id)


def count_points(gameID):
    global period
    global possession
    global ft1
    global ft2

    game = pbp[pbp.Game_id == gameID]
    for row in game.itertuples():
        if row.Period != period:
            period += 1
            change_lineup(gameID, period)
        # count possessions
        if possession != row.Team_id and (row.Team_id == team_oneID or row.Team_id == team_twoID):
            if row.Team_id == team_oneID:
                for player in on_court1:
                    team_one_off[player][1] += 1
                    team_one_def[player][1] += 1
                possession = row.Team_id
            elif row.Team_id == team_twoID:
                for player in on_court2:
                    team_two_off[player][1] += 1
                    team_two_def[player][1] += 1
                possession = row.Team_id
        # get free throw lineup
        if row.Event_Msg_Type == 6 and (row.Action_Type == 2 or row.Action_Type == 9 or row.Action_Type == 11
                                        or row.Action_Type == 14 or row.Action_Type == 15 or row.Action_Type == 17):
            del ft1[:]
            del ft2[:]
            for player in on_court1:
                ft1.append(player)
            for player in on_court2:
                ft2.append(player)
        # count points
        if row.Person1 not in team_one_off and row.Person1 not in team_two_off:
            continue
        if row.Person1 in team_one_off:
            if row.Event_Msg_Type == 8:
                on_court1.remove(row.Person1)
                on_court1.append(row.Person2)
            if row.Event_Msg_Type == 1:
                for player in on_court1:
                    team_one_off[player][0] += row.Option1
                for player in on_court2:
                    team_two_def[player][0] += row.Option1
            if row.Event_Msg_Type == 3:
                for player in ft1:
                    team_one_off[player][0] += row.Option1
                for player in ft2:
                    team_two_def[player][0] += row.Option1
        if row.Person1 in team_two_off:
            if row.Event_Msg_Type == 8:
                on_court2.remove(row.Person1)
                on_court2.append(row.Person2)
            if row.Event_Msg_Type == 1:
                for player in on_court2:
                    team_two_off[player][0] += row.Option1
                for player in on_court1:
                    team_one_def[player][0] += row.Option1
            if row.Event_Msg_Type == 3:
                for player in ft2:
                    team_two_off[player][0] += row.Option1
                for player in ft1:
                    team_one_def[player][0] += row.Option1


def result(gameID, out):
    for player in team_one_off:
        if team_one_off[player][1] != 0:
            off = 100.0 * team_one_off[player][0] / team_one_off[player][1]
            team_one[player][0] = round(off, 2)
        else:
            team_one[player][0] = 0
    for player in team_one_def:
        if team_one_def[player][1] != 0:
            deff = 100.0 * team_one_def[player][0] / team_one_def[player][1]
            team_one[player][1] = round(deff, 2)
        else:
            team_one[player][1] = 0
    for player in team_two_off:
        if team_two_off[player][1] != 0:
            off = 100.0 * team_two_off[player][0] / team_two_off[player][1]
            team_two[player][0] = round(off, 2)
        else:
            team_two[player][0] = 0
    for player in team_two_def:
        if team_two_def[player][1] != 0:
            deff = 100.0 * team_two_def[player][0] / team_two_def[player][1]
            team_two[player][1] = round(deff, 2)
        else:
            team_two[player][1] = 0
    with open(out, 'w') as output:
        for key in team_one:
            output.write(gameID + ', ' + key + ', ' + str(team_one[key][0]) + ', ' + str(team_one[key][1]) + '\n')
        for key in team_two:
            output.write(gameID + ', ' + key + ', ' + str(team_two[key][0]) + ', ' + str(team_two[key][1]) + '\n')


def erase():
    global team_oneID
    global team_twoID
    global period
    global possession
    team_one.clear()
    team_two.clear()
    team_one_off.clear()
    team_one_def.clear()
    team_two_off.clear()
    team_two_def.clear()
    del on_court1[:]
    del on_court2[:]
    del ft1[:]
    del ft2[:]
    team_oneID = 'A'
    team_twoID = 'B'
    period = 1
    possession = 'S'


def main():
    count_game()
    index = 1
    test = []
    test.append('f959bc122b1ee996f3e12bc61c068ad4') # game 81
    test.append('9892e70d668a7287f5460350b8a6afdf') #game 42
    for game in games:
        initialize(game)
        count_points(game)
        output = 'games' + str(index) + '.txt'
        result(game, output)
        erase()
        index += 1

# still missing game 81
if __name__ == '__main__':
    main()
