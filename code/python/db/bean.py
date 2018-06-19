from sqlalchemy import Column, String, Sequence, Integer, create_engine, DATETIME, DateTime
from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine('sqlite:///../db.sqlite3', echo=True)
engine = create_engine("mysql+pymysql://root:123456@localhost:3306/testpymysql?charset=utf8", echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    # id = Column(Integer, primary_key=True)
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)


class ModifyRecord(Base):
    __tablename__ = 'ModifyRecord'
    id = Column(Integer, Sequence('diagnosis_norepeat_id_seq'), primary_key=True)
    # mtime  = DATETIME(storage_format="%(year)04d/%(month)02d/%(day)02d %(hour)02d:%(min)02d:%(second)02d",
    #           regexp=r"(\d+)/(\d+)/(\d+) (\d+)-(\d+)-(\d+)")
    timestamp = Column(DateTime, nullable=False) #datetime.now()
    operator = Column(String(32))
    fromold = Column(String(255))
    tonew = Column(String(255))
    originalid = Column(Integer)
# <th>日期</th>      <th>操作者</th>      <th>原来</th>      <th>更改为</th>


Base.metadata.create_all(engine)


