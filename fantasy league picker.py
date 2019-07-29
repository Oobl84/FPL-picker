"""
Rank players by scoring metric - points to value ratio. 
#Overall vs next 5 games, replace if next 5 games estimated points < estimated points - 4. Unless free transfers.

Separate by position? Top x players with limitations on budget and picks
budget limits:
    - Min cost to fill team: cheapest players, replace those already picked.
    - Estimated points
    - If budget - player value < cost to fill team then next player.
    - Aim maximise team total points.

Player past performance - rank by points scored.
Points by team difficulty
Poisson pts distribution vs form
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
sns.set()

players_1920 = pd.read_csv(r"C:\Users\ruban\OneDrive\Documents\Spyder Files\FPL Picker\players_1920_clean.csv", index_col=0)
cols = players_1920.columns.tolist()

points_top_players = players_1920.sort_values('total_points',ascending=False)
roi_top_player = players_1920.sort_values('value_ratio', ascending=False)
cheap_players = players_1920.loc[players_1920['now_cost'] <= 50].sort_values(['now_cost','total_points'], ascending=False)
cheap_players_sum = cheap_players[0:4]['now_cost'].sum()

def get_fantasy_squad(dframe, budget=1000, star_limit=3 , overspend=20.0, min_cost= 45.0):
    squad_count = 0
    fantasy_team = pd.DataFrame(columns=cols)
    star_limit = star_limit
    positions = {'gk' : 2, 'df': 5, 'mf': 5, 'fw' : 3}
    team_limits= {'ARS': 3, 'AVL': 3,'BOU': 3, 'BHA': 3,'BUR': 3,'CHE': 3,'CRY': 3,'EVE': 3,'LEI': 3,'LIV': 3,'MCI': 3,'MUN': 3,'NEW': 3,'NOR': 3,'SHU': 3,'SOU': 3,'TOT': 3,'WAT': 3,'WHU': 3,'WOL': 3}
    while squad_count < 15:
        for index, row in points_top_players.iterrows():
            if (len(fantasy_team) < star_limit) and (row.status == 'a') and (budget >= row.now_cost) and (positions[row.position] > 0) and (team_limits[row.team_name] > 0):
                fantasy_team = fantasy_team.append(row)
                positions[row['position']] = positions[row['position']] - 1
                budget -= row.now_cost
                team_limits[row.team_name] -= 1
                squad_count += 1
            else:
                while squad_count < 15:
                    for index, row in roi_top_player.iterrows():
                        if ((row.code in fantasy_team) == False) and (budget >= row.now_cost) and ((row.now_cost - (budget /(15-squad_count))) < overspend) and (row.status == 'a') and (positions[row.position] > 0) and (team_limits[row.team_name] > 0):
                            fantasy_team = fantasy_team.append(row)
                            budget -= row.now_cost
                            positions[row.position] = positions[row.position] - 1
                            team_limits[row.team_name] -= 1
                            squad_count += 1
                        else:
                            while squad_count < 15:
                                for index, row in cheap_players.iterrows():
                                    if ((row.code in fantasy_team) == False) and (budget >= row.now_cost) and ((budget/(15-squad_count)) >= min_cost) and (row.status == 'a') and (positions[row.position] > 0) and (team_limits[row.team_name] > 0):
                                        fantasy_team = fantasy_team.append(row)
                                        budget -= row.now_cost
                                        positions[row.position] = positions[row.position] - 1
                                        team_limits[row.team_name] -= 1
                                        squad_count += 1
                                    else:
                                        while squad_count < 15:
                                            if (budget/(15-squad_count)) < 45:
                                                print("out of money")
                                                final_team = fantasy_team[['full_name', 'position','team_name','total_points', 'now_cost']]
                                                total_points = final_team.total_points.sum()
                                                total_budget = final_team.now_cost.sum()
                                                return final_team, total_points, total_budget
                                            else:
                                                for index, row in cheap_players.iterrows():
                                                    if ((row.code in fantasy_team) == False) and (budget >= row.now_cost) and (row.status == 'a') and (positions[row.position] > 0) and (team_limits[row.team_name] > 0):
                                                        fantasy_team = fantasy_team.append(row)
                                                        budget -= row.now_cost
                                                        positions[row.position] = positions[row.position] - 1
                                                        team_limits[row.team_name] -= 1
                                                        squad_count += 1
                                
    final_squad = fantasy_team
    total_points = final_squad.total_points.sum()
    total_budget = final_squad.now_cost.sum()
    return {'squad' :final_squad, 'points': total_points, 'team_limits': team_limits, 'budget': total_budget}

def squad_refiner(squad):
    
    df = pd.DataFrame(squad['squad'].sort_values('total_points'))
    budget = 1000 - squad['budget']
    df_new = pd.DataFrame(columns=cols)
    
    for i in range(len(df)):
        team_limits = squad['team_limits']
        pos_pool = players_1920.loc[players_1920['position'] == df.position.values[i]].sort_values('total_points', ascending=False)

        replace_pool = pos_pool[(pos_pool['code'] != df.code.values[i]) & (pos_pool['total_points'] > df.total_points.values[i]) & (pos_pool['now_cost'] <= (budget + df.now_cost.values[i]))]
        replace_row = replace_pool[replace_pool['total_points'] == replace_pool['total_points'].max()]
        
    
    return df_new
    
#    for i in range(len(df)):
#        team_limits = squad['team_limits']
#        pos_pool = players_1920.loc[players_1920['position'] == df.position.values[i]].sort_values('total_points', ascending=False)
        
#        for j in range(len(pos_pool)):
            
#            if (pos_pool.code.values[j] not in df) & (pos_pool.code.values[j] not in df_new) & (team_limits[pos_pool.team_name.values[j]] > 0) & (pos_pool.total_points.values[j] > df.total_points.values[i]) & (pos_pool.now_cost.values[j] <= budget + df.now_cost.values[i]):
#                df_new = df_new.append(pos_pool.iloc[j])
#                budget += (df['now_cost'].values[i] - pos_pool['now_cost'].values[j])
 #               team_limits[df['team_name'].values[i]] -= 1
  #              team_limits[pos_pool['team_name'].values[i]] += 1
   #             break
    #        else:
     #           pass
    #return df_new, df_new['total_points'].sum(), df_new['now_cost'].sum()
    

