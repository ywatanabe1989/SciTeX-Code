![PyPI](https://img.shields.io/pypi/v/sql_manager)
![GitHub last commit](https://img.shields.io/github/last-commit/suqingdong/sql_manager)

# A simple database manager with sqlalchemy

### Installation
```bash
python3 -m pip install sql_manager
```

### Basic Usage
```python
from sqlalchemy import Column, Integer, String
from sql_manager import DynamicModel, Manager

# create model
columns = {
    'uid': Column(Integer, primary_key=True, comment='the unique identity'),
    'name': Column(String(10), comment='the username', default='zoro')}

Data = DynamicModel('OnePiece', columns, 'user')

print(Data.get_table())
'''
+------+---------------------+-------------+-----------------------+
| Key  | Comment             | Type        | Default               |
+------+---------------------+-------------+-----------------------+
| uid  | the unique identity | INTEGER     | None                  |
| name | the username        | VARCHAR(10) | ColumnDefault('zoro') |
+------+---------------------+-------------+-----------------------+
'''

data = Data(uid=1, name='luffy')
print(data)
'''
OnePiece <{'uid': 1, 'name': 'luffy'}>
'''

# insert one data
with Manager(Data, dbfile='test.db') as m:
    m.insert(Data(uid=1, name='luffy'))
    m.insert(dict(uid=2, name='zoro'))
'''
[2022-02-15 09:29:20 Manager insert DEBUG MainThread:98] >>> insert data: OnePiece <{'uid': 1, 'name': 'luffy'}>
[2022-02-15 09:29:20 Manager insert DEBUG MainThread:98] >>> insert data: OnePiece <{'uid': 2, 'name': 'zoro'}>
[2022-02-15 09:29:20 Manager __exit__ DEBUG MainThread:35] database closed.
'''

# insert multiple datas [slow for big data]
with Manager(Data, dbfile='test.db') as m:
    datas = [Data(uid=uid, name=name) for uid, name in zip([3, 4, 5], ['sanji', 'chopper', 'nami'])]
    m.insert(datas, key='uid')
'''
[2022-02-15 09:31:14 Manager insert DEBUG MainThread:98] >>> insert data: OnePiece <{'uid': 3, 'name': 'sanji'}>
[2022-02-15 09:31:14 Manager insert DEBUG MainThread:98] >>> insert data: OnePiece <{'uid': 4, 'name': 'chopper'}>
[2022-02-15 09:31:14 Manager insert DEBUG MainThread:98] >>> insert data: OnePiece <{'uid': 5, 'name': 'nami'}>
[2022-02-15 09:31:14 Manager __exit__ DEBUG MainThread:35] database closed.
'''

# insert bulk objects
with Manager(Data, dbfile='test.db') as m:
    bulk_datas = [Data(uid=uid, name='demo') for uid in range(6, 100000)]
    m.insert_bulk(bulk_datas)
'''
[2022-02-15 09:31:59 Manager insert_bulk DEBUG MainThread:114] >>> inserted 99994 objects ...
[2022-02-15 09:32:00 Manager __exit__ DEBUG MainThread:35] database closed.
'''
    
# insert bulk mappings
with Manager(Data, dbfile='test.db') as m:
    bulk_datas = [dict(uid=uid, name='demo') for uid in range(100001, 200000)]
    m.insert_bulk(bulk_datas)
'''
[2022-02-15 09:32:26 Manager insert_bulk DEBUG MainThread:117] >>> inserted 99999 mappings ...
[2022-02-15 09:32:26 Manager __exit__ DEBUG MainThread:35] database closed.
'''

# query, delete
with Manager(Data, dbfile='test.db') as m:
    res = m.query('uid', 1)
    print(res.all())
    m.delete('uid', 2)    
'''
[OnePiece <{'name': 'luffy', 'uid': 1}>]
[2022-02-15 09:55:27 Manager delete DEBUG MainThread:75] delete 1 row(s)
[2022-02-15 09:55:27 Manager __exit__ DEBUG MainThread:35] database closed.
'''


# use methods of raw session
with Manager(Data, dbfile='test.db') as m:
    query = m.session.query(Data)
    res = query.filter(Data.name.like('%op%')).limit(1)
    print(res)
    print(res.all())
'''
SELECT user.uid AS user_uid, user.name AS user_name 
FROM user 
WHERE user.name LIKE ?
 LIMIT ? OFFSET ?
[OnePiece <{'name': 'chopper', 'uid': 4}>]
[2022-02-15 09:56:44 Manager __exit__ DEBUG MainThread:35] database closed.
''' 
```

### Document
https://sql-manager.readthedocs.io/en/latest/
