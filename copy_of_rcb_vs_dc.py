# -*- coding: utf-8 -*-
"""Copy of RCB VS DC

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kEUh5onHBE_M3Fs8NDv2qowuus4dPmjz
"""



import pandas as pd

from google.colab import files
uploaded = files.upload()

deliveries_df = pd.read_csv('innings_deliveries.csv')

deliveries_df.head()

import matplotlib.pyplot as plt
import seaborn as sns

#data preparation for run distribution per over
run_distribution = deliveries_df.groupby(['team', 'over']).agg({'runs_total': 'sum'}).reset_index()

run_distribution

#ploting run distribution per over for both teams

plt.figure(figsize=(14, 6))
sns.lineplot(data=run_distribution, x='over', y='runs_total', hue='team', markers='o')
plt.title('Run Distribution per over')
plt.xlabel('over number')
plt.ylabel('runs scored')
plt.xticks(range(0, 12))
plt.legend(title='team')
plt.show()

#Next analyze the top scorers for each to highlight individual performance .
#lets create a bar chart to visualize the top contributors in terms of runs

top_scorers = deliveries_df.groupby(['team', 'batter']).agg({'runs_batter': 'sum'}).reset_index().sort_values(by='runs_batter', ascending=False)

top_scorers

plt.figure(figsize=(14, 8))
sns.barplot(data=top_scorers, x='runs_batter', y='batter', hue='team', dodge=False)
plt.xlabel('Top Scorers from each team')
plt.ylabel('batter')
plt.legend(title='team', loc='center right')
plt.show()

#prepaing data for bowling analysis
#deliveries_df['wicket_taken'] = deliveries_df['wicket_kind'].notna().astype(int)
# notna() is a Series of boolean values (True/False)
#.astype(int), you are converting this boolean Series into an integer Series. True values become 1 and False values become 0
#bowling_stats = deliveries_df.groupby(['team', 'bowler']).agg({'runs_total': 'sum', 'wicket_taken':'sum', 'over': 'nunique'}).reset_index()
#bowling_stats

#bowling_stats

#calculating economy rate (total runs conceded / number of over bowled)
#bowling_stats['economy_rate'] =bowling_stats['runs_total'] / bowling_stats['over']

#bowling_stats['economy_rate']

#display(bowling_stats[['bowler', 'economy_rate']])

#prepaing data for bowling analysis
deliveries_df['wicket_taken'] = deliveries_df['wicket_kind'].notna().astype(int)
# notna() is a Series of boolean values (True/False)
#.astype(int), you are converting this boolean Series into an integer Series. True values become 1 and False values become 0
bowling_stats = deliveries_df.groupby(['team', 'bowler']).agg({'runs_total': 'sum', 'wicket_taken':'sum', 'over': 'nunique'}).reset_index()

#calculating economy rate (total runs conceded / number of over bowled)
bowling_stats['economy_rate'] =bowling_stats['runs_total'] / bowling_stats['over']

#sorting the data for better visualization
bowling_stats_sorted = bowling_stats.sort_values(by = 'wicket_taken', ascending = False)

bowling_stats_sorted

#create the plot
fig, ax1 = plt.subplots(figsize=(14, 8))

#barplot for wicets
sns.barplot(data= bowling_stats_sorted, x='bowler', y='wicket_taken', hue='team',ax = ax1, alpha=0.6)#alpha=0.6 makes the bars 60% visible (or 40% transparent
ax1.set_ylabel('wicket taken')
ax1.set_xlabel('bowler')
ax1.set_title('Bowling Analysis: wickets and Economy Rate')
ax1.legend(title='team', bbox_to_anchor=(1.05, 1), loc='upper left')
#marker='o' puts circles on the line; sort=False keeps the data order as is.

for item in ax1.get_xticklabels():
  item.set_rotation(90)

ax2 =ax1.twinx()
sns.lineplot(data=bowling_stats_sorted, x='bowler', y='economy_rate', marker='o', sort=False, ax=ax2, color='black')
ax2.set_ylabel('Economy Rate')

plt.tight_layout()
plt.show()

#wicket dismissal types like:-lbw,bowled,runout,caught
#It was tells about the pitch condition

dismissal_types = deliveries_df['wicket_kind'].value_counts()

plt.figure(figsize=(8, 8))
plt.pie(dismissal_types, labels=dismissal_types.index, autopct='%1.1f%%', startangle=90)
plt.title("Type of wicets")
plt.show()

"""No lets perform partnership analysis by calculating and visualizing the most productive batting partneship in the match .we 'll look at runs scored per partnership and how long each partnership lasted in terms of all balls faced."""

#function t calculate partnership
def calculate_partnerships(df):
  partnerships = []
  current_partnership = {}
  for i, row in df.iterrows():
    if i == 0 :#or (row['batter] not in cuurent_patnership.values()):
      if current_partnership:
        partnerships.append(current_partnership)
      current_partnership = {
          'team': row['team'],
          'batter1': row['batter'],
          'batter2': row['non_striker'],
          'runs': 0,
          'balls': 0
      }
  current_partnership['runs'] += row['runs_total']
  current_partnership['balls'] += 1
  if 'player_out' in row and pd.notna(row['player_out']):
     if row['player_out'] == current_partnership['batter1']: #or row['player_out] == current_partnership['batter2]
      partnerships.append(current_partnership)
      current_partnership={}


#append last partnership if not ended by a wicket
  if current_partnership:
    partnerships.append(current_partnership)
  return partnerships

  #calculate partnership
partnerships_data = calculate_partnerships(deliveries_df)
partnerships_df = pd.DataFrame(partnerships_data)

#filternout significant partnerships (eg.., partnership ith more than 20 runs)
significant_partnerships = partnerships_df[partnerships_df['runs'] > 20]

#sort by highest runs
significant_partnerships = significant_partnerships.sort_values(by='runs', ascending=False)

plt.figure(figsize=(12, 8))
sns.barplot(data=significant_partnerships, x='runs', y='batter1', hue='team', dodge=False)
plt.title('significant Batting partnerships')
plt.xlabel('runs scored')
plt.ylabel('batter 1 (partnership initiated)')
plt.legend(title='team')
plt.show()

"""**OR**

"""

# Alternative approach to calculate partnerships
def get_partnership_key(row):
    # Create a unique key for each batting partnership, sorting batter names to handle strike changes
    batters = sorted([row['batter'], row['non_striker']])
    return f"{row['team']}_{batters[0]}_{batters[1]}"

deliveries_df['partnership_key'] = deliveries_df.apply(get_partnership_key, axis=1)

# Calculate partnership stats by grouping by the unique partnership key
partnerships_df = deliveries_df.groupby('partnership_key').agg(
    team=('team', 'first'),
    batter1=('batter', lambda x: x.mode()[0]), # Get the most frequent batter1 in the partnership or ,get_mode_value for both batter 1, batter 2
    batter2=('non_striker', lambda x: x.mode()[0]), # Get the most frequent batter2 in the partnership
    runs=('runs_total', 'sum'),
    balls=('over', 'count') # Count of deliveries in the partnership
).reset_index()

# Drop the partnership_key as it's no longer needed
partnerships_df = partnerships_df.drop(columns=['partnership_key'])

# Sort partnerships by runs scored
partnerships_df_sorted = partnerships_df.sort_values(by='runs', ascending=False)

display(partnerships_df_sorted)

# Filter for significant partnerships (e.g., partnerships with more than 20 runs)
significant_partnerships = partnerships_df_sorted[partnerships_df_sorted['runs'] > 20]

# Create the bar plot
plt.figure(figsize=(12, 8))
sns.barplot(data=significant_partnerships, x='runs', y='batter1', hue='team', dodge=False)
plt.title('Significant Batting Partnerships')
plt.xlabel('Runs Scored')
plt.ylabel('Batter 1') # Using batter1 as a representative for the partnership
plt.legend(title='Team')
plt.show()

#function to classify the phase of the game based on the over number

def classify_phase(over):
  if over < 6:
    return 'powerplay'
  elif over < 16:
    return 'middle'
  else:
    return 'Death overs'

#adding phase information to the data frame
deliveries_df['phase'] = deliveries_df['over'].apply(classify_phase)

#grouping data by phase and team to calculate runs and wickets
phase_analysis = deliveries_df.groupby(['team' , 'phase']).agg({'runs_total': 'sum', 'wicket_taken': 'sum', 'over': 'count'}).rename(columns={'over' : 'balls'}).reset_index()

#calucuating the run rate
phase_analysis['run_rate'] = phase_analysis['runs_total'] / phase_analysis['balls']

#ploting the phase analysis
fig, ax1 = plt.subplots(figsize=(12, 8))

#bar plot for runs scored in each phase
sns.barplot(data=phase_analysis, x='phase', y='runs_total', hue='team', ax=ax1)
ax1.set_title('phase analysis : runs and wickets')
ax1.set_ylabel('total runs')
ax1.set_xlabel('match phase')

#line plot for wickets lost
ax2 = ax1.twinx()
sns.lineplot(data=phase_analysis, x='phase', y='wicket_taken', hue='team', marker='o', ax=ax2, legend=False)
ax2.set_ylabel('wickets lost')

plt.show()

#Now lets calcuate the strikreate of tghe batters

#calculate runs ans balla faced for each batter
batter_stats = deliveries_df.groupby('batter').agg({'runs_batter': 'sum', 'over': 'count'}).rename(columns={'over': 'balls_faced'}).reset_index()

#caluculate strike rate for each batter (runs per 100 balls)
batter_stats['strike_rate'] = (batter_stats['runs_batter'] / batter_stats['balls_faced']) * 100

# sorting batters by their strike rate
batter_stats_sorted = batter_stats.sort_values(by='strike_rate', ascending=False)

batter_stats_sorted

#now lets drive deeper by looking at how strie rate varied with the phase of the game

#merging phase information with batter stats
batter_phase_stats = deliveries_df.groupby(['batter' , 'phase']).agg({'runs_batter': 'sum', 'over': 'count'}).rename(columns={'over': 'balls_faced'}).reset_index()

batter_phase_stats['strike_rate'] = (batter_phase_stats['runs_batter'] / batter_phase_stats['balls_faced']) * 100

#filltering top performer based on overall strike rate
top_performers = batter_stats_sorted.head(5)['batter']
batter_phase_stats_top = batter_phase_stats[batter_phase_stats['batter'].isin(top_performers)]

batter_phase_stats_top

plt.figure(figsize=(12, 8))
sns.barplot(data=batter_phase_stats_top, x='batter', y='strike_rate', hue='phase')
plt.title('strike rate of top batters in each phase')
plt.xlabel('batter')
plt.ylabel('strike rate')
plt.legend(title='match phase')
plt.show()

deliveries_df.head()

# calculate cumulative runs and wickets for each ball for both teams
deliveries_df['cumulative_runs'] = deliveries_df.groupby('team')['runs_total'].cumsum()
deliveries_df['cumulative_wickets'] = deliveries_df.groupby('team')['wicket_taken'].cumsum()

# separate data for both teams
rcb_deliveries = deliveries_df[deliveries_df['team'] == 'Royal Challengers Bengaluru']
dc_deliveries = deliveries_df[deliveries_df['team'] == 'Delhi Capitals']

# calculating overs for cumulative analysis
rcb_deliveries['over_ball'] = rcb_deliveries['over'] + (rcb_deliveries.groupby('over').cumcount() + 1) / 6
dc_deliveries['over_ball'] = dc_deliveries['over'] + (dc_deliveries.groupby('over').cumcount() + 1) / 6

# plotting cumulative run rates and wickets
fig, ax = plt.subplots(figsize=(14, 8))

# plot for RCB
ax.plot(rcb_deliveries['over_ball'], rcb_deliveries['cumulative_runs'], color='blue', label='RCB Runs')
ax.scatter(rcb_deliveries[rcb_deliveries['wicket_taken'] == 1]['over_ball'], rcb_deliveries[rcb_deliveries['wicket_taken'] == 1]['cumulative_runs'], color='blue', marker='X', s=100)

# plot for DC
ax.plot(dc_deliveries['over_ball'], dc_deliveries['cumulative_runs'], color='red', label='DC Runs')
ax.scatter(dc_deliveries[dc_deliveries['wicket_taken'] == 1]['over_ball'], dc_deliveries[dc_deliveries['wicket_taken'] == 1]['cumulative_runs'], color='red', marker='X', s=100)

ax.set_title('Cumulative Runs with Wickets for RCB and DC')
ax.set_xlabel('Over')
ax.set_ylabel('Cumulative Runs')
ax.legend()
plt.show()

# calculate runs and wickets per over for both teams
per_over_stats = deliveries_df.groupby(['team', 'over']).agg({'runs_total': 'sum', 'wicket_taken': 'sum'}).reset_index()

# calculate run rate for each over
per_over_stats['run_rate'] = (per_over_stats['runs_total'] / 6)    # Runs per over to runs per ball (standard rate)

# separate data for RCB and DC for plotting
rcb_per_over_stats = per_over_stats[per_over_stats['team'] == 'Royal Challengers Bengaluru']
dc_per_over_stats = per_over_stats[per_over_stats['team'] == 'Delhi Capitals']

# plotting run rates and marking wickets for each team
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# RCB
ax1.plot(rcb_per_over_stats['over'], rcb_per_over_stats['run_rate'], marker='o', color='blue', label='RCB Run Rate')
ax1.scatter(rcb_per_over_stats[rcb_per_over_stats['wicket_taken'] > 0]['over'], rcb_per_over_stats[rcb_per_over_stats['wicket_taken'] > 0]['run_rate'], color='red', s=100, label='Wickets')
ax1.set_title('RCB Run Rate Per Over')
ax1.set_ylabel('Run Rate (Runs per ball)')
ax1.legend()

# DC
ax2.plot(dc_per_over_stats['over'], dc_per_over_stats['run_rate'], marker='o', color='red', label='DC Run Rate')
ax2.scatter(dc_per_over_stats[dc_per_over_stats['wicket_taken'] > 0]['over'], dc_per_over_stats[dc_per_over_stats['wicket_taken'] > 0]['run_rate'], color='blue', s=100, label='Wickets')
ax2.set_title('DC Run Rate Per Over')
ax2.set_xlabel('Over')
ax2.set_ylabel('Run Rate (Runs per ball)')
ax2.legend()

plt.show()

