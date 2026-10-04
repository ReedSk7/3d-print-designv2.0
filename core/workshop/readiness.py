"""Read-only app readiness without optional Bambu or printer operations."""
import sys
import subprocess
from pathlib import Path
from core.environment import dependency_checks
from core.workflow.openscad import find_openscad, openscad_version

def check_readiness(root:Path):
    checks=[{'name':'Python','status':'pass' if (3,12)<=sys.version_info[:2]<=(3,13) else 'fail','detail':sys.version.split()[0]}]
    checks.extend(dependency_checks(root))
    try:
        executable=find_openscad()
        checks.append({'name':'OpenSCAD','status':'pass','detail':openscad_version(executable),'path':str(executable)})
    except (OSError,RuntimeError,subprocess.TimeoutExpired) as exc:
        checks.append({'name':'OpenSCAD','status':'fail','detail':str(exc),'corrective_action':'Select an installed compiler using OPENSCAD_PATH.'})
    checks.append({'name':'app assets','status':'pass' if (root/'app/dist/index.html').is_file() else 'fail','detail':'Built local app assets required.','corrective_action':'Build the isolated app with npm run build.'})
    return {'ready':all(item['status']=='pass' for item in checks),'interpreter':sys.executable,'checks':checks,'printer_connection':'not attempted'}
