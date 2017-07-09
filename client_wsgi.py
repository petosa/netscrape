from netscrape_client.client import get_app
if __name__ == "__main__":
    app, CLIENT_PORT = get_app()
    app.run(host="0.0.0.0", port=CLIENT_PORT)