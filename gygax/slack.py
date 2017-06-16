import requests
from bs4 import BeautifulSoup
from ..util.config import config
from slackclient import SlackClient
auth_token = config.apiSlack.token
default_data = dict(token=auth_token)

def build_url(ext):
	return config.apiSlack.base + ext

def reqOk(resp):
	if resp.json() and resp.json().get('ok'):
		return True
	return False

class Slack:
	@staticmethod
	def _get_dms():
		resp = requests.post(build_url(config.apiSlack.dm_list),
							data = default_data)
		if resp.json().get('ok'):
			return resp.json().get('ims')

	@staticmethod
	def _get_dm_user(user):
		for dm in Slack._get_dms():
			if dm['user'] == user:
				return dm['id']
	
	@staticmethod
	def _get_user_id(user):
		resp = requests.post(build_url(config.apiSlack.user_list),
							data = default_data)
		if resp.json().get('ok'):
			users = resp.json().get('members')
			for u in users:
				if u['name'] == user:
					return u['id']

	@staticmethod
	def _create_dm(user):
		data = dict(user=user)
		data.update(default_data)
		resp = requests.post(build_url(config.apiSlack.dm_new),
							data = data)
		if reqOk(resp):
			return resp.json().get('channel', {}).get('id')
		return None

	@staticmethod
	def dm(user, message):
		user_id = Slack._get_user_id(user)
		if not user_id:
			raise Exception('could not resolve user.')
		dm = Slack._get_dm_user(user_id)
		if not dm:
			dm = Slack._create_dm(user_id)
		if not dm:
			raise Exception('could not create direct message.')
		data = dict(channel = dm, text = message)
		data.update(default_data)
		resp = requests.post(build_url(config.apiSlack.post_msg),
							data = data)
		if reqOk(resp):
			return True
		return False

