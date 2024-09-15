def upgrade(connection):
    connection.executescript('''
        ALTER TABLE Subscribers
        ADD COLUMN color_mode VARCHAR(3) NOT NULL DEFAULT 'dfm';
    ''')
    connection.commit()

def downgrade(connection):
    connection.executescript('''
        ALTER TABLE Subscribers
        DROP COLUMN color_mode;
    ''')
    connection.commit()
