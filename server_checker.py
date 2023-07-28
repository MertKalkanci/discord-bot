from mcstatus import JavaServer

def minecraft_server_checker(ip, port = 25565):
    try:
        server = JavaServer.lookup(f"{ip}:{port}")
        status = server.status()
        return f"Server is online, with {status.players.online}/{status.players.max} players online.\n ping: {status.latency}ms"
    except Exception as e:
        print("error: ", e)
        return "It seems that server is offline or port not forwarded etc."
