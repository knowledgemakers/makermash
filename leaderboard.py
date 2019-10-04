import csv
from datetime import date

class Leaderboard:

    leaderboard=[]
    highscorers = []
    top5score = 0

    def __init__(self):

        with open("leaderboard.csv") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                self.leaderboard.append({
                    "date": row[0],
                    "name": row[1],
                    "score": int(row[2])
                })
            if len(self.leaderboard)>0:
                self.leaderboard.sort(key=lambda x: x["score"], reverse=True)
            if len(self.leaderboard)>5:
                self.highscorers = self.leaderboard[:5]
            else:
                self.highscorers=self.leaderboard
            if len(self.highscorers)>0:
                self.top5score = self.highscorers[len(self.highscorers)-1]["score"]

    def write(self, name, score):
        today = date.today()
        with open("leaderboard.csv", "a") as file:
            writer= csv.writer(file)
            writer.writerow([today, name, score])
        if self.is_highscore(score):
            self.highscorers.append({
                    "date": str(today),
                    "name": name,
                    "score": int(score)
                })
            self.highscorers.sort(key=lambda x: x["score"], reverse=True)
            self.highscorers = self.highscorers[:5]
            self.top5score = self.highscorers[len(self.highscorers)-1]["score"]


    def is_highscore(self, score):
        return int(score) > int(self.top5score)

    def get_highscore_string(self):
        highscore_table = "---HIGHSCORE---\n"
        for high in self.highscorers:
            highscore_table += (high["date"] + "     " + high["name"] + "     " + str(high["score"]) + "\n")
        return highscore_table













