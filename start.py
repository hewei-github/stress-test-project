import os

port = "80"
host = "https://mp.weixin.qq.com"

if __name__ == "__main__":
    command = "locust --host=" + host + " --port=" + port + " -f " + "locustfile.py"
    print(command)
    print("open http://localhost:" + port)
    os.system(command)
