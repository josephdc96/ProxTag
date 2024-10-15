import requests

from config import Config


class PVE:
    def __init__(self, config: Config):
        self.config = config
        self.client = requests.Session()
        self.client.headers = {
            'Authorization': f'PVEAPIToken={self.config.token}'
        }
        self.client.verify = self.config.ssl
        self.api_url = f'{self.config.host}:{self.config.port}/api2/json'

    def get_vms(self):
        url = f'{self.api_url}/cluster/resources?type=vm'
        request = requests.get(url, headers=self.client.headers)
        json = request.json()
        return json['data']

    def get_vm_config(self, node, id):
        url = f'{self.api_url}/nodes/{node}/qemu/{id}/config'
        request = requests.get(url)
        json = request.json()
        return json['data']

    def get_vm_status(self, node, id):
        url = f'{self.api_url}/nodes/{node}/qemu/{id}/status/current'
        request = requests.get(url)
        json = request.json()
        return json['data']

    def start_vm(self, node, id):
        url = f'{self.api_url}/nodes/{node}/qemu/{id}/status/start'
        request = requests.post(url)
        return request.status_code

    def shutdown_vm(self, node, id):
        url = f'{self.api_url}/nodes/{node}/qemu/{id}/status/shutdown'
        request = requests.post(url)
        return request.status_code

    def restart_vm(self, node, id):
        url = f'{self.api_url}/nodes/{node}/qemu/{id}/status/restart'
        request = requests.post(url)
        return request.status_code

    def pause_vm(self, node, id):
        url = f'{self.api_url}/nodes/{node}/qemu/{id}/status/pause'
        request = requests.post(url)
        return request.status_code

    def suspend_vm(self, node, id):
        url = f'{self.api_url}/nodes/{node}/qemu/{id}/status/suspend'
        request = requests.post(url)
        return request.status_code

    def stop_vm(self, node, id):
        url = f'{self.api_url}/nodes/{node}/qemu/{id}/status/stop'
        request = requests.post(url)
        return request.status_code

    def reset_vm(self, node, id):
        url = f'{self.api_url}/nodes/{node}/qemu/{id}/status/reset'
        request = requests.post(url)
        return request.status_code
