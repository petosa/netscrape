from netscrape.server import get_app
if __name__ == "__main__":
    app, SERVER_PORT = get_app()
    app.run(host="0.0.0.0", port=SERVER_PORT)