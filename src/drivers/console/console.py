from os import system, name

from src.drivers.display import Display


def clear():

    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

class Console(Display):
    def __init__(self, controller):
        self.controller = controller

    def initialize(self):
        clear()
        self.controller.launch()

    def display_vms(self, vms):
        clear()
        while True:
            print("Current Virtual Machines:")
            for vm in vms:
                try:
                    name = vm["name"]
                except KeyError:
                    name = "Unknown"
                print(f'{vm["vmid"]}\t{name}\t{vm["status"]}')
            print("\nEnter VM id or type 'exit' to exit")
            resp = input("> ")
            if resp == 'exit':
                break
            try:
                resp = int(resp)
                for vm in vms:
                    if vm["vmid"] == resp:
                        break
                else:
                    x = None

                if vm is None:
                    print("VM not found")
                    continue

                self.controller.display_vm(vm["node"], vm["vmid"])
            except ValueError:
                print("Please enter valid VM id")

    def display_vm(self, vm, status, node, id):
        clear()
        cont = True
        while cont:
            print(f'Current Virtual Machine: {vm["name"]}')
            print()
            print("Options:")
            opt = 1
            if status["status"] == "running":
                print("\t1: Shut Down VM")
                print("\t2: Reboot VM")
                print("\t3: Pause VM")
                print("\t4: Hibernate VM")
                print("\t5: Stop VM")
                print("\t6: Reset VM")
                opt = 7
            else:
                print("\t1: Start VM")
                opt = 2
            print(f"\t{opt}: Go Back")
            resp = input("> ")

            try:
                resp = int(resp)
                if status["status"] == "running":
                    match resp:
                        case 1:
                            self.controller.shutdown_vm(node, id)
                        case 2:
                            self.controller.reboot_vm(node, id)
                        case 3:
                            self.controller.suspend_vm(node, id)
                        case 4:
                            self.controller.suspend_vm(node, id)
                        case 5:
                            self.controller.stop_vm(node, id)
                        case 6:
                            self.controller.reset_vm(node, id)
                        case 7:
                            cont = False
                        case _:
                            print("Invalid option")
                else:
                    match resp:
                        case 1:
                            self.controller.start_vm(node, id)
                        case 2:
                            cont = False
                        case _:
                            print("Invalid option")
            except ValueError:
                print("Please enter valid option")