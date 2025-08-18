import random

def round_robin_schedule(teams):
    """Generate a round robin schedule for an even number of teams."""
    if len(teams) % 2:
        teams.append('BYE')  # If odd number of teams
    
    n = len(teams)
    schedule = []

    # Copy teams to rotate
    teams = teams[:]

    for round_num in range(n - 1):
        pairs = []
        for i in range(n // 2):
            t1 = teams[i]
            t2 = teams[n - 1 - i]
            if t1 != 'BYE' and t2 != 'BYE':
                pairs.append((t1, t2))
        schedule.append(pairs)
        # Rotate teams but keep first team fixed
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    
    return schedule
    
# Read and clean team names
with open('list_squads.dat') as file:
    teams = [line.strip() for line in file]

# Save the first 3 teams before shuffling
important_teams = teams[:3]

random.shuffle(teams)

# Split into 4 groups of 8
groups = [teams[i:i+8] for i in range(0, 24, 8)]

# Swap important teams into first position of groups 1, 2, 3
for i in range(3):
    # Find where the important team is now
    for gi in range(3):
        if important_teams[i] in groups[gi]:
            idx = groups[gi].index(important_teams[i])
            found = True
            break
    if found:
        groups[gi][idx], groups[i][0] = groups[i][0], groups[gi][idx]
    else:
        print(f"Warning: team {important_teams[i]} not found in any group")

t1=[]
t2=[]
t3=[]
t4=[]
# Print groups
for idx, group in enumerate(groups, 1):
	print(f"\nGroup {idx}:")
	for team in group:
		if idx==1:
			t1.append(team)
		if idx==2:
			t2.append(team)
		if idx==3:
			t3.append(team)
		#if idx==4:
		#	t4.append(team)
		print(f"  - {team}")

        



## Example usage:
##teams = ['Team1', 'Team2', 'Team3', 'Team4', 'Team5', 'Team6', 'Team7', 'Team8']
#
match_days = round_robin_schedule(t1)
# Print the schedule
for day_num, matches in enumerate(match_days, 1):
    print(f"Match Day {day_num}:")
    for t1, t2 in matches:
        print(f"  {t1} vs {t2}")
    print()
