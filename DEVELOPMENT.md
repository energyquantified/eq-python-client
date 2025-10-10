# Development notes

Make sure you have **Python 3.10 or higher** installed. Preferably, you should
use some kind of virtual environment.

Using **virtualenv** and **virtualenvwrapper**:

```bash
# Make virtual environment
mkvirtualenv -p $(which python3.10) --no-site-packages eq-python-client

# Active an environment later on (unless already activated)
workon eq-python-client

# Install requirements
pip install -r requirements.txt
```
