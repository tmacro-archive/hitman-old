from game import Hitman
from uuid import uuid4

def test_Hitman(l):
	users = [uuid4().hex for x in range(l)]
	weapons = [x for x in range(l)]
	locations = [users[x] + str(weapons[x]) for x in range(l)]
	state = Hitman.create_game(users, weapons, locations)


if __name__ == '__main__':
	for x in range(100):
		test_Hitman(x)
		if x%10 == 0:
			print('Finished %s tests'%x)
