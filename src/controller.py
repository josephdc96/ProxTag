from drivers.display import Display
from config import Config
from pve import PVE

class Controller:
    def __init__(self, config: Config):
        self.node = None
        self.display = None
        self.config = config
        self.pve = PVE(config)

    def set_display(self, display: Display) -> None:
        self.display = display

    def launch(self, node = None):
        self.node = node
        self.display_vms()

    def display_vms(self):
        vms = self.pve.get_vms()
        self.display.display_vms(vms)

    def display_vm(self, node, id):
        vm = self.pve.get_vm_config(node, id)
        status = self.pve.get_vm_status(node, id)
        if vm is None or status is None:
            raise Exception("VM not found")
        self.display.display_vm(vm, status, node, id)

    def start_vm(self, node, id):
        return self.pve.start_vm(node, id)

    def stop_vm(self, node, id):
        return self.pve.stop_vm(node, id)

    def restart_vm(self, node, id):
        return self.pve.restart_vm(node, id)

    def shutdown_vm(self, node, id):
        return self.pve.shutdown_vm(node, id)

    def reset_vm(self, node, id):
        return self.pve.reset_vm(node, id)

    def pause_vm(self, node, id):
        return self.pve.pause_vm(node, id)

    def suspend_vm(self, node, id):
        return self.pve.suspend_vm(node, id)