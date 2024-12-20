import os
from ssp import create_app

os.environ["FLASK_APP"] = "run.py"
app = create_app()



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080, debug=True)