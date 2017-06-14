import random

class Hitman:
	@staticmethod
	def _create_hits(users, weapons, locations):
		hits = []
		for user in users:
			w = weapons.pop(weapons.index(random.choice(weapons)))
			l = locations.pop(locations.index(random.choice(locations)))
			hits.append((user,w,l))
		return hits
		  
	@staticmethod
	def _assign_hits(users, hits):
		assigned = {}
		for user in users[:]:
			h = random.choice(hits)
			if h[0] == user or assigned.get(h[0],[None])[0] == user:
				if len(hits) > 1:
					assigned.update(Hitman._assign_hits(users,hits))
					return assigned
			assigned[user] = h
			hits.remove(h)
			users.remove(user)
		return assigned

	@staticmethod
	def	create_game(users, weapons, locations):
		hits = Hitman._create_hits(users, weapons, locations)
		return Hitman._assign_hits(users, hits)

			
