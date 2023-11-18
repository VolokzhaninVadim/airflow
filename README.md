# Airflow
![airflow_64x64_emoji_transparent.png](https://cwiki.apache.org/confluence/download/attachments/145723561/airflow_64x64_emoji_transparent.png)

## Generate FERNET_KEY
```python
from cryptography.fernet import Fernet
FERNET_KEY = Fernet.generate_key().decode()
print(FERNET_KEY)
```
## Useful scripts
```python
# Export variables
airflow variables export variables.txt
```
## Backup
For backup use [backup-server](https://github.com/VolokzhaninVadim/duplicati).

