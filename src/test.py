from pyamaze import maze, COLOR, agent

m = maze()
m.CreateMaze(theme=COLOR.light)
a = agent(m, 5, 5)

m.run()
