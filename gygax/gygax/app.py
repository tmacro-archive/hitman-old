from .util.config import config
import sqlalchemy
from sqlalchemy.orm import sessionmaker

# Create database
db = sqlalchemy.create_engine('sqlite:///test.db', echo = False)

Session = sessionmaker()
Session.configure(bind = db)

from .models import Base
Base.metadata.bind = db

# Build tables
Base.metadata.create_all(db)

from .bot.agent import Agent
from .api.slack import Slack

agent = Agent()
# agent.start()

# app.start()
slack = Slack(agent.put)

from .bot.action import CommandAction
cmd_action = CommandAction(agent.proxy)

from .bot.action import RegisterAction
reg_action = RegisterAction(agent.proxy)

from .bot.action import SendMessageAction
msg_action = SendMessageAction(agent.proxy)

from .bot.action import ValidateSlackAction
valid_action = ValidateSlackAction(agent.proxy)

from .bot.action import CollectInfoAction
col_action = CollectInfoAction(agent.proxy)

from .bot.action import SetInfoAction
set_action = SetInfoAction(agent.proxy)

