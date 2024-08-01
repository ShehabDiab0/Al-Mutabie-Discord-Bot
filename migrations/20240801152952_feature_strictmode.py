def upgrade(connection):
    connection.executescript('''
        ALTER TABLE Subscribers
        ADD COLUMN strict_mode INTEGER NOT NULL DEFAULT 1;
    ''')
    connection.commit()

def downgrade(connection):
    connection.executescript('''
        ALTER TABLE Subscribers
        DROP COLUMN strict_mode;
        
    ''')
    connection.commit()
