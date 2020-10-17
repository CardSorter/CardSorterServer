from flaskr.app import application

# Creates an application object for the Gunicorn server.
if __name__ == "__main__":
  application.run()