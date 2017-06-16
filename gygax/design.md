## So I have this bot, Now What?
### What does this bot need to do?

* register new users
* collect game info
* start a new game
* collect kills
* confirm kills
* determine winner
* react to player commands to view/update info

### What tools does this bot need to do its job

* send slack messages
* recieve slack messages
* authenticate slack user -> uid using http api
* http api to recieve webhooks
* persistent storage via sqldb

### So how is this bot going to accomplish its goals using those tools

* register user
	* recieve `@bot register` via slack
	* `POST` to auth with slack, to recieve token
	* send slack private message to user confirming register
* collect game info
	* send info notice w/ command help
	* recieve `!weapon set` or `!location set`
	* update database
	* echo updated information vie slack
* start a new game
	* monitor number of free players
	* generate starting state
	* update database
	* notify players of inital state via slack
* collect kills
	* recieve `!report kill` via slack
		* mark hit as pending
		* init confirm
	* recieve `!report override` via slack
		* if correct
			* mark hit as confirmed
		* if wrong
			* 3 tries, then reporter dies
* confirm kill
	* send confirmation msg to target via slack
	* recieve `!confirm` or `!deny`
	* if confirm
		* mark hit as complete
		* assign new hit
	* if deny
		* notify reporter of deny prompt for override
* determine the winner
	* monitor confirmed deaths
	* if one man standing
		* user wins
		* notify everyone via slack
* react to player commands
	* monitor slack
	* respond via slack