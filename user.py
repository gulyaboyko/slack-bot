
class User:
    id = ""
    name = ""
    group = ""

    def __init__(self, user_data):
        self.id = user_data['id']
        self.name = user_data['name']
        self.group = user_data['group']

    def __init__(self, user_id, name, group):
        self.id = user_id
        self.name = name
        self.group = group

    @staticmethod
    def from_array(users_dict_array):
        users: [User] = []
        for user_data in users_dict_array:
            users.append(User(user_data))
        return users
