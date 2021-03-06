"""
This example showcases special postgres features
"""
import asyncio
from copy import copy

from asyncpg import InvalidCatalogNameError

from tortoise import Tortoise, fields
from tortoise.backends.asyncpg.client import AsyncpgDBClient
from tortoise.models import Model
from tortoise.utils import generate_schema


class Report(Model):
    id = fields.IntField(pk=True)
    content = fields.JSONField()

    def __str__(self):
        return str(self.id)


CONNECTION_PARAMS = {
    'host': 'localhost',
    'port': '54325',
    'user': 'tortoise',
    'password': 'qwerty123',
    'database': 'tortoise',
}


async def run():
    client = AsyncpgDBClient(single_connection=True, **CONNECTION_PARAMS)
    test_db_name = CONNECTION_PARAMS['database'] + '_test'
    await client.create_connection()

    try:
        await client.execute_script('DROP DATABASE {}'.format(test_db_name))
    except InvalidCatalogNameError:
        pass
    await client.execute_script(
        'CREATE DATABASE {} OWNER {}'.format(test_db_name, CONNECTION_PARAMS["user"])
    )
    await client.close()
    test_db_connection_params = copy(CONNECTION_PARAMS)
    test_db_connection_params['database'] = test_db_name

    client = AsyncpgDBClient(single_connection=True, **test_db_connection_params)
    await client.create_connection()
    Tortoise.init(client)
    await generate_schema(client)

    report_data = {
        'foo': 'bar',
    }
    print(await Report.create(content=report_data))
    print(await Report.filter(content=report_data).first())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
