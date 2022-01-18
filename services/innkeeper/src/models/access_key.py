from src.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import desc
from src.config import Config


class AccessKey(db.Model):
    __tablename__ = "access_key"
    __table_args__ = {"schema": Config.PSQL_SCHEMA}

    id = db.Column(
        UUID(as_uuid=True),
        server_default=db.text("public.gen_random_uuid()"),
        primary_key=True,
    )

    password = db.Column(db.String(200))
    permissions = db.Column(db.JSON(none_as_null=True))
    is_admin = db.Column(db.Boolean(), default=False)
    is_active = db.Column(db.Boolean(), default=False)

    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    tenant_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(f"{Config.PSQL_SCHEMA}.tenant.id"),
    )

    @classmethod
    def get_all_by_tenant(cls, tenant_id, page, per_page):

        query = cls.query.filter_by(tenant_id=tenant_id)

        return query.order_by(desc(cls.created_at)).paginate(
            page=page, per_page=per_page
        )

    @classmethod
    def get_by_is_admin(cls, is_admin):
        return cls.query.filter_by(is_admin=is_admin).first()

    @classmethod
    def get_by_is_active(cls, is_active):
        return cls.query.filter_by(is_active=is_active).first()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()
