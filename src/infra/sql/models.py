# from sqlalchemy.dialects.postgresql import
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.sql.db_init import Base

# Промежуточная M:M организация-деятельность
organization_activity = Table(
    "organization_activity",
    Base.metadata,
    Column(
        "organization_id",
        Integer,
        ForeignKey("organizations.id"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        Integer,
        ForeignKey("activities.id"),
        primary_key=True,
    ),
)


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)

    # Relates
    phones: Mapped[list["PhoneModel"]] = relationship(
        "PhoneModel",
        back_populates="organization",
        cascade="all, delete-orphan",
        uselist=True,
    )
    activities: Mapped[list["ActivityModel"]] = relationship(
        "ActivityModel",
        secondary=organization_activity,
        back_populates="organizations",
        uselist=True,
    )
    building: Mapped["BuildingModel"] = relationship(
        "BuildingModel",
        back_populates="organizations",
    )


class BuildingModel(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(index=True)
    latitude: Mapped[float]
    longitude: Mapped[float]

    organizations: Mapped[list[OrganizationModel]] = relationship(
        OrganizationModel,
        back_populates="building",
        uselist=True,
    )


class ActivityModel(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    level: Mapped[int] = mapped_column(server_default="1", default=1)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("activities.id"),
        nullable=True,
    )
    organizations: Mapped[list["OrganizationModel"]] = relationship(
        OrganizationModel,
        secondary=organization_activity,
        back_populates="activities",
        uselist=True,
    )


class PhoneModel(Base):
    __tablename__ = "phones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    number: Mapped[str] = mapped_column(String(16))

    organization = relationship(OrganizationModel, back_populates="phones")
