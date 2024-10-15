from abc import abstractmethod


class Display:
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def display_vms(self, vms):
        pass

    @abstractmethod
    def display_vm(self, vm, status, node, id):
        pass