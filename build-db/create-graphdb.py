import json
from neo4j import GraphDatabase


class CreateDB:

	def __init__(self, uri, user, password, contact_data):
		# self.driver = GraphDatabase.driver(uri, auth=(user, password))
		self.driver = GraphDatabase.driver(uri)
		self.contacts = contact_data


	def close(self):
		self.driver.close()


	def add_chats(self, chats):
		with self.driver.session() as session:
			for group in chats:
				results = session.execute_write(self._create_chats, group)

			print('DONE!!!')

			return
		
	@staticmethod
	def _create_chats(tx, group):
		group_id = group["id"]["user"]

		print(f'Adding Group: {group["name"]} - {group_id}')

		result = tx.run("CREATE (a:Group {id:$id,name:$name})"
			"RETURN a.name + ', from node ' + id(a)",
			name=group["name"],
			id=group_id)

		group_members = group['groupMetadata']['participants']
		print('Creating Group Contacts:', len(group_members))
		for group_member in group_members:
			phone_number = group_member["id"]["user"]

			if phone_number == '972586800450':
				continue

			contact = find_contact(phone_number)
			contact_name = get_name_from_contact(contact)

			result = tx.run("MERGE (c:Contact {id:$user, user:$user, isMyContact:$isMyContact})"
				"\nON CREATE SET c.name = $name"
				"\nWITH c as contact"
				"\nMATCH(g:Group{id:$group_id})"
				"\nCREATE (contact)-[:IS_PARTICIPANT_OF {isAdmin:$isAdmin, isSuperAdmin:$isSuperAdmin}]->(g)"
				"\nRETURN contact.id + ', from node ' + id(contact)",
				user=phone_number, 
				name = contact_name,
				group_id = group_id,
				isAdmin = group_member["isAdmin"],
				isSuperAdmin = group_member["isSuperAdmin"],
				isMyContact = contact['isMyContact']
			)


		return


def read_json():
	# Opening JSON file
	f = open('../data/chats.json')

	# returns JSON object as
	# a dictionary
	data = json.load(f)

	# Closing file
	f.close()

	# filter only for groups
	groups = [
		dict for dict in data
		if dict['isGroup'] is True
	]	

	return groups

def read_json_contacts():
	# Opening JSON file
	f = open('../data/contact.json')

	# returns JSON object as
	# a dictionary
	data = json.load(f)

	# Closing file
	f.close()

	return data

def find_contact(number):
	filter_contacts = [
		c for c in contact_data
		if c.get('number') == number
	]

	return filter_contacts[0]

def get_name_from_contact(cnt):
	if is_blank(cnt.get('name')) is not None:
		return cnt.get('name')
	elif is_blank(cnt.get('verifiedName')) is not None:
		return cnt.get('verifiedName')
	elif is_blank(cnt.get('pushname')) is not None:
		return cnt.get('pushname')

	return None		
	
def is_blank(txt):
	if txt is None or txt == '' or len(txt) < 3:
		return None
	
	return txt

if __name__ == "__main__":
	json_data = read_json()
	global contact_data
	contact_data = read_json_contacts()

	print(f'Chats count: {len(json_data)}')

	greeter = CreateDB("bolt://localhost:7687/whatsappdb", "neo4j", "password", contact_data)
	greeter.add_chats(json_data)
	greeter.close()
