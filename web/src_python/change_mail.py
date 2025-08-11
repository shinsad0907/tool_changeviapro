import subprocess

def get_id_machine(ldplayer_path):
    result = subprocess.run([f'{ldplayer_path}\ldconsole.exe', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout.strip()
    # Mỗi dòng trong output đại diện cho một máy ảo
    vm_list = output.splitlines()
    if vm_list:
        # Lấy ID của máy ảo đầu tiên (giả sử ID là phần đầu tiên của mỗi dòng)
        return vm_list