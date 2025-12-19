import subprocess
import gzip
import sys
import shutil
from datetime import datetime
from pathlib import Path
import json
def backup_mysql(DB_HOST, DB_NAME, DB_USER, DB_PASS, output_dir="backup_data"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{DB_NAME}_{timestamp}.sql.gz"

    # Check if mysqldump is available
    if not shutil.which("mysqldump"):
        print("mysqldump not found. Ensure MySQL client tools are installed and in PATH.")
        sys.exit(1)

    dump_cmd = [
        "mysqldump",
        "-h", DB_HOST,
        "-u", DB_USER,
        f"-p{DB_PASS}",
        "--single-transaction",    
        "--skip-lock-tables",          
        DB_NAME
    ]

    try:
        # Run mysqldump
        with subprocess.Popen(dump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as dump_proc:
            with gzip.open(output_file, "wb") as f_out:
                for chunk in iter(lambda: dump_proc.stdout.read(4096), b""):
                    f_out.write(chunk)

            stderr = dump_proc.stderr.read()
            if dump_proc.returncode is None:
                dump_proc.wait()

        if dump_proc.returncode != 0:
            print("mysqldump failed with error:")
            print(stderr.decode())
            sys.exit(1)

        print(f"Backup created successfully: {output_file}")
        # json logging
        backup_record = {
            "database": DB_NAME,
            "timestamp": timestamp,
            "file_path": output_file.as_posix(),
            "file_name": output_file.name,
            "status": "success"
        }

        log_file = output_dir / "backups.json"

        # read existing log
        if log_file.exists():
            with open(log_file, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        # append new record
        logs.append(backup_record)

        # write back
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=4)

    except Exception as e:
        print(f"Backup failed: {e}")
        sys.exit(1)

