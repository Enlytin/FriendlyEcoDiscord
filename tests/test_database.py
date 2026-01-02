import sys
import os
import pytest
import pytest_asyncio


from economy_db import DatabaseManager 

TEST_DB_NAME = ":memory:"

@pytest_asyncio.fixture
async def db():
    """
    Fixture that handles the lifecycle of the DB connection.
    1. Setup: Creates object, opens connection, creates tables.
    2. Yield: Gives the object to the test.
    3. Teardown: Closes the connection after test is done.
    """
    database = DatabaseManager(TEST_DB_NAME)
    
    # SETUP
    await database.connect()     # Open persistent connection
    await database.initialize()  # Create tables in that RAM connection
    
    yield database               # Run the test
    
    # TEARDOWN
    await database.close()       # Close (wiping the RAM DB)

@pytest.mark.asyncio
async def test_create_account(db):
    user_id = 12345
    start_bal = 100
    
    initial = await db.get_balance(user_id)
    assert initial is None

    await db.create_account(user_id, start_bal)
    
    balance = await db.get_balance(user_id)
    assert balance == start_bal

@pytest.mark.asyncio
async def test_update_balance(db):
    user_id = 999
    await db.create_account(user_id, 0)
    
    await db.update_balance(user_id, 50)
    assert await db.get_balance(user_id) == 50

    await db.update_balance(user_id, -20)
    assert await db.get_balance(user_id) == 30