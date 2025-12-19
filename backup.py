import subprocess
import datetime

backup_file = f"osu_dos_backup_{datetime.date.today()}.sql"


subprocess.run([
    "pg_dump",
    "-U", "postgres",
    "-F", "c",
    "-f", backup_file,
    "osudos" 
])
print(f"Бэкап создан: {backup_file}")
