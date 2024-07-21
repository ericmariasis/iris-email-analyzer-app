from python import create_app
from python.myconfig import *
from flaskext.markdown import Markdown

if __name__ == "__main__":
    database_uri = f'iris://{DB_USER}:{DB_PASS}@{DB_URL}:{DB_PORT}/{DB_NAMESPACE}'
    app = create_app(database_uri)
    Markdown(app)
    app.run(debug=True, host='0.0.0.0', port=4040)