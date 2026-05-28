from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    property_type = db.Column(db.String(50), default='house')
    status = db.Column(db.String(20), default='vacant')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contracts = db.relationship(
        'Contract', backref='property', lazy='dynamic',
        cascade='all, delete-orphan', order_by='Contract.created_at.desc()'
    )
    photos = db.relationship(
        'Photo', backref='property', lazy='dynamic',
        cascade='all, delete-orphan', order_by='Photo.created_at.desc()'
    )
    rental_histories = db.relationship(
        'RentalHistory', backref='property', lazy='dynamic',
        cascade='all, delete-orphan', order_by='RentalHistory.start_date.desc()'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'type': self.property_type,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Property {self.name}>'


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    tenant_name = db.Column(db.String(200), nullable=False)
    tenant_id_card = db.Column(db.String(50))
    tenant_phone = db.Column(db.String(50))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    rent_amount = db.Column(db.Float, nullable=False)
    deposit = db.Column(db.Float)
    file_path = db.Column(db.String(500))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Contract {self.tenant_name} @ {self.property_id}>'


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    photo_type = db.Column(db.String(20), default='outdoor')
    file_path = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Photo {self.id} {self.photo_type}>'


class RentalHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    tenant_name = db.Column(db.String(200), nullable=False)
    tenant_id_card = db.Column(db.String(50))
    tenant_phone = db.Column(db.String(50))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    rent_amount = db.Column(db.Float, nullable=False)
    deposit = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RentalHistory {self.tenant_name}>'


# All required columns per table for schema repair
_REQUIRED_COLUMNS = {
    'contract': [
        ('property_id', 'INTEGER'),
        ('tenant_name', 'VARCHAR(200)'),
        ('tenant_id_card', 'VARCHAR(50)'),
        ('tenant_phone', 'VARCHAR(50)'),
        ('start_date', 'DATE'),
        ('end_date', 'DATE'),
        ('rent_amount', 'FLOAT'),
    ],
    'rental_history': [
        ('property_id', 'INTEGER'),
        ('tenant_name', 'VARCHAR(200)'),
        ('tenant_id_card', 'VARCHAR(50)'),
        ('tenant_phone', 'VARCHAR(50)'),
        ('start_date', 'DATE'),
        ('rent_amount', 'FLOAT'),
    ],
}


def schema_repair(database):
    """Add any missing columns to existing SQLite tables (safe re-run)."""
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(database.engine)
        for table, columns in _REQUIRED_COLUMNS.items():
            existing = {c['name'] for c in inspector.get_columns(table)}
            for col_name, col_type in columns:
                if col_name not in existing:
                    with database.engine.connect() as conn:
                        conn.execute(text(
                            f'ALTER TABLE {table} ADD COLUMN {col_name} {col_type}'
                        ))
                        conn.commit()
    except Exception:
        pass  # table may not exist yet
