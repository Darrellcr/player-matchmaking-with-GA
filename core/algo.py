import random

from player import Team

# SELECTION START
def roulette_wheel_selection(team_pool, num_teams):
    selected_teams = []
    for _ in range(num_teams):
        total_fitness = sum(team.fitness for team in team_pool)
        if total_fitness == 0:
            total_fitness = 1
        fitness = [team.fitness for team in team_pool]
        p = [f / total_fitness for f in fitness]

        selected_team = random.choices(team_pool, weights=p, k=1)
        team_pool.remove(selected_team[0])
        selected_teams.append(selected_team[0])
    return selected_teams, team_pool


teamPool = []
for _ in range(10):
    team = Team(_ + 1)
    teamPool.append(team)

for data in teamPool:
    print("========= Team " + str(data.id) + " =========")
    print("MMR: " + str(data.mmr))
    print("Fitness: " + str(data.fitness))

new_teams = []
if len(teamPool) > 0 and len(teamPool) % 2 == 0:
    while teamPool:
        selected_teams, teamPool = roulette_wheel_selection(teamPool, 2)
        for team in selected_teams:
            new_teams.append(team)
else:
    while len(teamPool) > 1:
        selected_teams, teamPool = roulette_wheel_selection(teamPool, 2)
        for team in selected_teams:
            new_teams.append(team)

print("======== PARENT =======")
for team in new_teams:
    print("Selected team ID:", team.id)
    print("Selected team MMR:", team.mmr)
    print("Selected team fitness:", team.fitness)

print()
print("====== OLD TEAMS ======")

for data in teamPool:
    print("========= Team " + str(data.id) + " =========")
    print("MMR: " + str(data.mmr))
    print("Fitness: " + str(data.fitness))
    
# SELECTION END
