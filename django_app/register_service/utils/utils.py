import exrex


def generate_numbers():
    file_path = "register_service/utils/patterns.txt"
    with open(file_path, "r") as file:
        patterns = file.read().splitlines()

        numbers = []
        for pattern in patterns:
            num = list(exrex.generate(pattern[2:]))
            numbers.extend(num)

        return numbers


def generate_proxy():
    ips = read_proxy("register_service/utils/proxies.txt")
    proxys = [
        {"ip": ip, "port_http_https": "50100", "port_socks5": "50101", "username": "vnderlord", "password": "RJpx8JH8Ki"}
        for ip in ips
    ]
    return proxys

def read_proxy(filename):
    with open(filename, "r") as file:
        proxies = file.read().splitlines()

    return proxies
