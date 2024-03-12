# Update this method with the appropriate migration when needed
def upgrade():
    from .migration1_0 import upgrade

    upgrade()
