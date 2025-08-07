from DailyLogAI import DailyLogAI

ai = DailyLogAI()

query = "Patient eating log: Missed breakfast 3 times this week Binge eating episode on Wednesday Ate dinner with family twice Avoided carbs 4 days Self-reported guilt after eating 2 days of >1200 calories, rest ~800 Other info: Female, 17 years old 3 months post-discharge (anorexia nervosa)"
response = ai.queryLLM(query)
print(response.encode('utf-8', errors='replace').decode())
