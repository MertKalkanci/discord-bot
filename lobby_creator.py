import random

def create_teams(player_list, team_number = 2):
    random.shuffle(player_list)
    teams = []
    team_player_count = (int) (len(player_list) / team_number)

    for i in range(team_number):
        teams.append([])
        for j in range(team_player_count):
            if i * team_player_count + j < len(player_list):
                teams[i].append(player_list[i * team_player_count + j])

    
    return teams