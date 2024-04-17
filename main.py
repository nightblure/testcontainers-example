from contextlib import contextmanager

from sqlalchemy import create_engine, Column, String, Integer, DateTime, text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer


class Base(DeclarativeBase):
    pass


class TestEntity(Base):
    __tablename__ = 'test_entity'

    id = Column(Integer, primary_key=True, autoincrement=True)
    field = Column(String)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))


@contextmanager
def get_session_context(engine):
    try:
        maker = sessionmaker(bind=engine)
        session = maker()
        yield session
    except Exception as e:
        print(str(e))
        session.rollback()
    finally:
        session.close()


def main():
    user = 'admin'
    password = 'passw_o_rd'
    # host = 'localhost'
    # port = 5460
    db = 'test_db'
    # db_url = f'postgresql://{user}:{password}@{host}:{port}/{db}'

    with PostgresContainer(
            image='postgres:alpine3.19',
            username=user,
            password=password,
            dbname=db
    ) as pg:
        db_url = pg.get_connection_url()
        engine = create_engine(db_url)
        Base.metadata.create_all(bind=engine)

        with get_session_context(engine) as session:
            entities = [TestEntity(field=f'text_{i + 1}') for i in range(10)]
            session.add_all(entities)
            session.commit()

            entities = session.query(TestEntity).all()

            for entity in entities:
                entity.__dict__.pop('_sa_instance_state', None)
                print(entity.__dict__)


if __name__ == '__main__':
    main()
