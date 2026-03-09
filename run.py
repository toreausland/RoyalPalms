import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from app import app
app.run(debug=True, host='0.0.0.0', port=5000)
