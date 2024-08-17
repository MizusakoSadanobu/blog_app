from abc import ABC, abstractmethod

class AuthInterface(ABC):
    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    def login(self):
        pass

class PostInterface(ABC):
    @abstractmethod
    def create_post(self):
        pass

    @abstractmethod
    def edit_post(self, post):
        pass

    @abstractmethod
    def show_posts(self):
        pass

    @abstractmethod
    def delete_post(self, post):
        pass

    @abstractmethod
    def manage_users(self):
        pass
