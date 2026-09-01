from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.system_setting import SystemSetting


class SystemSettingsRepository:

    def get(
        self,
        db: Session,
        key: str
    ) -> str | None:

        statement = select(SystemSetting).where(
            SystemSetting.key == key
        )

        setting = db.execute(
            statement
        ).scalar_one_or_none()

        if not setting:
            return None

        return setting.value


    def set(
        self,
        db: Session,
        key: str,
        value: str
    ) -> None:

        statement = select(SystemSetting).where(
            SystemSetting.key == key
        )

        setting = db.execute(
            statement
        ).scalar_one_or_none()

        if setting:
            setting.value = value

        else:
            setting = SystemSetting(
                key=key,
                value=value
            )

            db.add(setting)

        db.commit()