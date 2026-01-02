import aiosqlite
import logging

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    async def connect(self):
        """Opens the connection and keeps it alive."""
        if not self.conn:
            self.conn = await aiosqlite.connect(self.db_name)
            # This line ensures standard SQL behavior for rows
            self.conn.row_factory = aiosqlite.Row 

    async def close(self):
        """Closes the connection safely."""
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def initialize(self):
        """Creates tables. Requires connect() to be called first."""
        if not self.conn:
            await self.connect()
            
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0
            )
        """)
        await self.conn.commit()
        logging.info("Database initialized.")

    async def get_balance(self, user_id: int):
        async with self.conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row['balance'] if row else None

    async def create_account(self, user_id: int, starting_balance: int):
        await self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", 
            (user_id, starting_balance)
        )
        await self.conn.commit()

    async def update_balance(self, user_id: int, amount: int):
        await self.conn.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?", 
            (amount, user_id)
        )
        await self.conn.commit()