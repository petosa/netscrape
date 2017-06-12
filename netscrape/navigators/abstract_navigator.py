from abc import ABC, abstractmethod

class abstract_navigator(ABC):

    @abstractmethod
    def execute(self, url):
        pass

    @abstractmethod
    def save(self, scraped_dict):
        pass

    @abstractmethod
    def reschedule(self, scheduler, period):
        pass
