
class User:
    id = ""
    name = ""
    group = ""
    command = ""
    email = ""
    is_active = False

    def __init__(self, user_data):
        self.id = user_data['id']
        self.name = user_data['name']
        self.group = user_data['group']
        self.command = user_data['command']
        self.email = user_data['email']
        self.is_active = user_data['isActive']

    def __init__(self, user_id, name, group, command, email, is_active):
        self.id = user_id
        self.name = name
        self.group = group
        self.command = command
        self.email = email
        self.is_active = is_active

    @staticmethod
    def from_array(users_dict_array):
        users: [User] = []
        for user_data in users_dict_array:
            users.append(User(user_data))
        return users
