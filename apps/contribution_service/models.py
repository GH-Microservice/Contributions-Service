from sqlalchemy import Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from database.contributions_db import ContributionsBASE
import datetime


class ContributionsModel(ContributionsBASE):
    __tablename__ = "contributions"

    id: Mapped[int] = mapped_column(Integer, index=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    repository_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today())
    commit_count: Mapped[int] = mapped_column(Integer, default=0)
    year: Mapped[int] = mapped_column(Integer, default=datetime.date.today().year)
