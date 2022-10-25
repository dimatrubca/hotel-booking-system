
from datetime import datetime, timedelta
from database import SessionLocal
import models
from settings import MAX_INACTIVE_TIME

def check_services_activity(db: SessionLocal) -> None:
    """ Pretend this function deletes expired tokens from the database """
    inactive_services = db.query(models.Service).filter(models.Service.updated_at <= datetime.now() - timedelta(seconds=MAX_INACTIVE_TIME))

    inactive_services.update({'is_active': False})#todo: check
    db.commit()

    