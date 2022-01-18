from extensions import db
from sqlalchemy import asc, desc
from sqlalchemy.dialects.postgresql import UUID
from config import Config


class Tenant(db.Model):
    __tablename__ = "tenant"
    __table_args__ = {"schema": Config.PSQL_SCHEMA}

    id = db.Column(
        UUID(as_uuid=True),
        server_default=db.text("public.gen_random_uuid()"),
        primary_key=True,
    )

    name = db.Column(db.String, nullable=False)
    wallet_id = db.Column(UUID(as_uuid=True), nullable=True)
    is_active = db.Column(db.Boolean(), default=False)

    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    access_keys = db.relationship("AccessKey", backref="tenant")

    @classmethod
    def get_by_is_active(cls, is_active):
        return cls.query.filter_by(is_active=is_active).first()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_by_wallet_id(cls, wallet_id):
        return cls.query.filter_by(wallet_id=wallet_id).first()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all_active(cls, q, page, per_page, sort, order):

        name = "%{name}%".format(name=q)

        if order == "asc":
            sort_logic = asc(getattr(cls, sort))
        else:
            sort_logic = desc(getattr(cls, sort))

        return (
            cls.query.filter(cls.name.ilike(name), cls.is_active.is_(True))
            .order_by(sort_logic)
            .paginate(page=page, per_page=per_page)
        )

    def save(self):
        db.session.add(self)
        db.session.commit()
